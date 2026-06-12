"""CLI for pipedoc."""

import os
import sys
from typing import Optional

import click

from pipedoc.agent import Agent


@click.group()
@click.version_option(prog_name="pipedoc")
def main() -> None:
    """pipedoc - AI DevOps agent for CI diagnostics and PR reviews."""
    pass


@main.command()
@click.argument("run_url")
@click.option("--token", envvar="GITHUB_TOKEN", help="GitHub PAT (default: $GITHUB_TOKEN)")
@click.option("--model", default="openai/gpt-4.1", help="LLM model name")
@click.option("--report", is_flag=True, help="Generate HTML report")
def analyze(run_url: str, token: Optional[str], model: str, report: bool) -> None:
    """Diagnose failed GitHub Actions pipeline runs with AI."""
    try:
        agent = Agent(github_token=token, model=model)
        
        # Connectivity check
        click.echo("🔗 Checking GitHub Models API connectivity...")
        if not agent.connectivity_check():
            click.secho("✗ Failed to connect to GitHub Models API", fg="red", err=True)
            sys.exit(1)
        click.secho("✓ Connected", fg="green")
        
        click.echo("\n📊 Analyzing pipeline failure...")
        result = agent.analyze(run_url)
        
        # Display results
        click.echo(f"\n{'=' * 60}")
        click.secho(f"Capability: {result['capability']}", fg="cyan", bold=True)
        click.echo(f"Findings: {len(result['findings'])}")
        click.echo(f"Reduction: {result['context']['reduction_pct']:.1f}%")
        click.echo(f"Tokens used: {result['tokens_used']} | Cost: ${result['cost_usd']:.4f}")
        click.echo(f"{'=' * 60}")
        
        for finding in result["findings"]:
            if hasattr(finding, "severity"):
                severity_color = {
                    "high": "red",
                    "med": "yellow",
                    "info": "blue",
                    "low": "cyan",
                }.get(finding.severity.value, "white")
                click.secho(f"\n[{finding.severity.value.upper()}]", fg=severity_color, bold=True, nl=False)
            click.echo(f" {finding.title}")
            if hasattr(finding, "detail"):
                click.echo(f"  {finding.detail}")
            if hasattr(finding, "suggested_fix") and finding.suggested_fix:
                click.secho(f"  💡 Fix: {finding.suggested_fix}", fg="green")
    
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@main.command()
@click.argument("pr_url")
@click.option("--token", envvar="GITHUB_TOKEN", help="GitHub PAT (default: $GITHUB_TOKEN)")
@click.option("--model", default="openai/gpt-4.1", help="LLM model name")
@click.option("--report", is_flag=True, help="Generate HTML report")
def review(pr_url: str, token: Optional[str], model: str, report: bool) -> None:
    """Review pull requests for bugs, security issues, and CI/K8s misconfigurations."""
    try:
        agent = Agent(github_token=token, model=model)
        
        # Connectivity check
        click.echo("🔗 Checking GitHub Models API connectivity...")
        if not agent.connectivity_check():
            click.secho("✗ Failed to connect to GitHub Models API", fg="red", err=True)
            sys.exit(1)
        click.secho("✓ Connected", fg="green")
        
        click.echo("\n📋 Reviewing pull request...")
        result = agent.review(pr_url)
        
        # Display results
        click.echo(f"\n{'=' * 60}")
        click.secho(f"Capability: {result['capability']}", fg="cyan", bold=True)
        click.echo(f"Findings: {len(result['findings'])}")
        click.echo(f"Reduction: {result['context']['reduction_pct']:.1f}%")
        click.echo(f"Tokens used: {result['tokens_used']} | Cost: ${result['cost_usd']:.4f}")
        click.echo(f"{'=' * 60}")
        
        for finding in result["findings"]:
            if hasattr(finding, "severity"):
                severity_color = {
                    "high": "red",
                    "med": "yellow",
                    "info": "blue",
                    "low": "cyan",
                }.get(finding.severity.value, "white")
                click.secho(f"\n[{finding.severity.value.upper()}]", fg=severity_color, bold=True, nl=False)
            click.echo(f" {finding.title}")
            if hasattr(finding, "detail"):
                click.echo(f"  {finding.detail}")
    
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@main.command()
@click.option("--token", envvar="GITHUB_TOKEN", help="GitHub PAT (default: $GITHUB_TOKEN)")
def check(token: Optional[str]) -> None:
    """Check GitHub Models API connectivity."""
    try:
        agent = Agent(github_token=token)
        click.echo("🔗 Checking GitHub Models API connectivity...")
        if agent.connectivity_check():
            click.secho("✓ Connected to GitHub Models API", fg="green")
            click.echo(f"Cache stats: {agent.cache_stats()}")
        else:
            click.secho("✗ Failed to connect to GitHub Models API", fg="red", err=True)
            sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
