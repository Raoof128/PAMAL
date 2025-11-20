
import requests
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

API_URL = "http://localhost:8000"
CURRENT_USER = "raouf"  # Mock user for CLI

def _handle_request_error(e: Exception) -> None:
    """Helper to handle connection errors gracefully."""
    console.print(f"[bold red]Connection Error:[/bold red] Could not connect to PAM API at {API_URL}.")
    console.print(f"[dim]Details: {e}[/dim]")
    raise typer.Exit(code=1)

@app.command()
def init() -> None:
    """Initialize the vault with some demo data."""
    secrets = [
        {
            "id": "linux-prod-01",
            "name": "Linux Production Server",
            "type": "linux",
            "value": "InitialPass123!",
            "metadata": {"host": "192.168.1.10", "username": "root", "role": "linux-admin"}
        },
        {
            "id": "win-db-01",
            "name": "Windows Database Server",
            "type": "windows",
            "value": "WinAdminPass!",
            "metadata": {"host": "192.168.1.20", "username": "Administrator", "role": "windows-admin"}
        }
    ]
    
    for s in secrets:
        try:
            r = requests.post(f"{API_URL}/secrets", json=s, headers={"X-User": CURRENT_USER})
            if r.status_code in [200, 201]:
                console.print(f"[green]Created secret: {s['id']}[/green]")
            else:
                console.print(f"[red]Failed to create {s['id']}: {r.text}[/red]")
        except requests.exceptions.RequestException as e:
            _handle_request_error(e)

@app.command()
def list() -> None:
    """List all secrets in the vault."""
    try:
        r = requests.get(f"{API_URL}/secrets", headers={"X-User": CURRENT_USER})
        if r.status_code != 200:
             console.print(f"[red]Error fetching secrets: {r.text}[/red]")
             return

        secrets = r.json()
        
        table = Table(title="Vault Secrets")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Last Rotated")

        for s in secrets:
            table.add_row(s['id'], s['name'], s['type'], s['last_rotated'])
        
        console.print(table)
    except requests.exceptions.RequestException as e:
        _handle_request_error(e)

@app.command()
def request(secret_id: str, reason: str = "Maintenance") -> None:
    """Request access to a secret."""
    payload = {"user": CURRENT_USER, "secret_id": secret_id, "reason": reason}
    try:
        r = requests.post(f"{API_URL}/request", json=payload)
        
        if r.status_code == 200:
            data = r.json()
            console.print(f"[bold green]Request Status: {data['status']}[/bold green]")
            if 'request_id' in data:
                console.print(f"Request ID: {data['request_id']}")
                if data['status'] == 'approved':
                     console.print(f"Use 'pamctl get {data['request_id']}' to retrieve password.")
        else:
            console.print(f"[red]Error: {r.text}[/red]")
    except requests.exceptions.RequestException as e:
        _handle_request_error(e)

@app.command()
def approve(request_id: str, user: str = "admin") -> None:
    """Approve a pending request (Admin only)."""
    payload = {"admin_user": user, "request_id": request_id, "decision": "APPROVED"}
    try:
        r = requests.post(f"{API_URL}/approve", json=payload)
        
        if r.status_code == 200:
            console.print(f"[green]Request {request_id} approved successfully.[/green]")
        else:
            console.print(f"[red]Error: {r.text}[/red]")
    except requests.exceptions.RequestException as e:
        _handle_request_error(e)

@app.command()
def get(request_id: str) -> None:
    """Retrieve a credential using a valid request ID."""
    try:
        r = requests.get(f"{API_URL}/credential/{request_id}", headers={"X-User": CURRENT_USER})
        
        if r.status_code == 200:
            data = r.json()
            console.print(f"[bold yellow]Password: {data['secret']}[/bold yellow]")
            console.print(f"Expires at: {data['expires_at']}")
        else:
            console.print(f"[red]Error: {r.text}[/red]")
    except requests.exceptions.RequestException as e:
        _handle_request_error(e)

@app.command()
def rotate(secret_id: str) -> None:
    """Manually trigger rotation for a secret."""
    try:
        r = requests.post(f"{API_URL}/rotate/{secret_id}", headers={"X-User": CURRENT_USER})
        if r.status_code == 200:
            console.print(f"[green]Successfully rotated {secret_id}[/green]")
        else:
            console.print(f"[red]Rotation failed: {r.text}[/red]")
    except requests.exceptions.RequestException as e:
        _handle_request_error(e)

@app.command()
def audit() -> None:
    """View audit logs."""
    try:
        r = requests.get(f"{API_URL}/audit")
        if r.status_code != 200:
             console.print(f"[red]Error fetching logs: {r.text}[/red]")
             return

        logs = r.json()
        
        table = Table(title="Audit Logs")
        table.add_column("Time", style="dim")
        table.add_column("User", style="cyan")
        table.add_column("Action", style="bold white")
        table.add_column("Secret", style="magenta")
        table.add_column("Success", style="green")

        for log in logs:
            table.add_row(
                log['timestamp'], 
                log['user'], 
                log['action'], 
                log.get('secret_id', '-'), 
                "Yes" if log['success'] else "No"
            )
        console.print(table)
    except requests.exceptions.RequestException as e:
        _handle_request_error(e)

if __name__ == "__main__":
    app()
