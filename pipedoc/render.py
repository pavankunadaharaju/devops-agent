"""Terminal and HTML rendering for pipedoc results."""

import tempfile
import webbrowser
from pathlib import Path
from typing import Optional

import click

from pipedoc.capabilities.base import Result


def render_result(result: Result, open_html: bool = False) -> None:
    """Render result to terminal and optionally HTML report.
    
    Args:
        result: Result object
        open_html: Whether to open HTML report in browser
    """
    render_terminal(result)
    # TODO: implement HTML rendering


def render_terminal(result: Result) -> None:
    """Render result to terminal with colors and badges.
    
    Args:
        result: Result object
    """
    click.echo("")
    click.secho("=" * 70, fg="cyan")
    click.secho(f"📊 {result.capability.upper()} Results", fg="cyan", bold=True)
    click.secho("=" * 70, fg="cyan")
    
    # Findings
    if result.findings:
        click.echo(f"\n🔍 Findings ({len(result.findings)}):")
        for i, finding in enumerate(result.findings, 1):
            # Severity badge
            severity_color = {
                "info": "blue",
                "low": "cyan",
                "med": "yellow",
                "high": "red",
            }.get(finding.severity.value, "white")
            
            click.secho(f"\n  {i}. [{finding.severity.value.upper()}]", fg=severity_color, bold=True, nl=False)
            click.echo(f" {finding.title}")
            
            # Detail
            if finding.detail:
                for line in finding.detail.split("\n"):
                    click.echo(f"     {line}")
            
            # Location
            if finding.location:
                click.secho(f"     📍 {finding.location}", fg="dim")
            
            # Suggested fix
            if finding.suggested_fix:
                click.secho(f"     💡 Fix: {finding.suggested_fix}", fg="green")
            
            # Cached badge
            if finding.cached:
                click.secho(" 💾 CACHED", fg="green", bold=True)
    else:
        click.secho("\n✓ No issues found!", fg="green")
    
    # Context reduction
    click.echo(f"\n📉 Context Reduction:")
    click.echo(f"   Raw: {result.context.metadata.get('raw_chars', 'N/A')} chars")
    click.echo(f"   Sent: {result.context.metadata.get('distilled_chars', 'N/A')} chars")
    click.secho(f"   Reduction: {result.context.reduction_pct:.1f}%", fg="green")
    
    # Telemetry
    click.echo(f"\n💰 Cost Telemetry:")
    click.echo(f"   Tokens used: {result.tokens_used}")
    click.echo(f"   Cost: ${result.cost_usd:.6f} USD")
    
    click.secho("=" * 70, fg="cyan")
    click.echo("")


def render_html(result: Result, output_path: Optional[Path] = None) -> str:
    """Render result to HTML report.
    
    Args:
        result: Result object
        output_path: Output file path (default: temp file)
        
    Returns:
        Path to HTML file
    """
    if not output_path:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_path = Path(f.name)
    
    # HTML template
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>pipedoc - {result.capability} Report</title>
    <style>
        body {{
            font-family: 'IBM Plex Mono', 'Courier New', monospace;
            background: #F7F8F2;
            color: #1E2A23;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border: 2px solid #1E2A23;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: #2E7D4F;
            color: white;
            padding: 20px;
            border-bottom: 2px solid #1E2A23;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .cost-strip {{
            background: #E4EFE1;
            padding: 15px 20px;
            border-bottom: 1px solid #1E2A23;
            display: flex;
            gap: 20px;
            font-size: 13px;
        }}
        .cost-item {{
            display: flex;
            flex-direction: column;
        }}
        .cost-label {{
            font-size: 11px;
            text-transform: uppercase;
            opacity: 0.7;
        }}
        .findings {{
            padding: 20px;
        }}
        .finding {{
            margin-bottom: 20px;
            padding: 15px;
            background: repeating-linear-gradient(
                90deg,
                #F7F8F2,
                #F7F8F2 10px,
                #E4EFE1 10px,
                #E4EFE1 20px
            );
            border-left: 4px solid;
            border-radius: 2px;
        }}
        .finding.high {{
            border-left-color: #C2362B;
        }}
        .finding.med {{
            border-left-color: #F5A623;
        }}
        .finding.low {{
            border-left-color: #4A90E2;
        }}
        .severity {{
            display: inline-block;
            padding: 4px 8px;
            margin-right: 10px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            border-radius: 2px;
        }}
        .severity.high {{
            background: #C2362B;
            color: white;
        }}
        .severity.med {{
            background: #F5A623;
            color: white;
        }}
        .severity.low {{
            background: #4A90E2;
            color: white;
        }}
        .finding-title {{
            font-weight: bold;
            font-size: 14px;
            margin: 10px 0;
        }}
        .finding-detail {{
            margin: 10px 0;
            font-size: 12px;
            line-height: 1.5;
        }}
        .suggested-fix {{
            background: #E4EFE1;
            padding: 10px;
            margin: 10px 0;
            border-left: 3px solid #2E7D4F;
            font-size: 12px;
        }}
        .cached {{
            display: inline-block;
            background: #2E7D4F;
            color: white;
            padding: 2px 6px;
            font-size: 10px;
            margin-left: 10px;
            border-radius: 2px;
        }}
        .footer {{
            background: #E4EFE1;
            padding: 15px 20px;
            border-top: 1px solid #1E2A23;
            font-size: 12px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {result.capability.upper()} Report</h1>
        </div>
        <div class="cost-strip">
            <div class="cost-item">
                <div class="cost-label">Raw Chars</div>
                <div>{result.context.metadata.get('raw_chars', 'N/A')}</div>
            </div>
            <div class="cost-item">
                <div class="cost-label">Sent Chars</div>
                <div>{result.context.metadata.get('distilled_chars', 'N/A')}</div>
            </div>
            <div class="cost-item">
                <div class="cost-label">Reduction</div>
                <div>{result.context.reduction_pct:.1f}%</div>
            </div>
            <div class="cost-item">
                <div class="cost-label">Tokens</div>
                <div>{result.tokens_used}</div>
            </div>
            <div class="cost-item">
                <div class="cost-label">Cost</div>
                <div>${result.cost_usd:.6f}</div>
            </div>
        </div>
        <div class="findings">
"""
    
    # Add findings
    for finding in result.findings:
        cached_badge = ' <span class="cached">💾 CACHED</span>' if finding.cached else ""
        fix_html = f'<div class="suggested-fix"><strong>💡 Fix:</strong> {finding.suggested_fix}</div>' if finding.suggested_fix else ""
        
        html_content += f"""
            <div class="finding {finding.severity.value}">
                <span class="severity {finding.severity.value}">{finding.severity.value.upper()}</span>
                <span class="finding-title">{finding.title}{cached_badge}</span>
                <div class="finding-detail">{finding.detail}</div>
                {fix_html}
            </div>
"""
    
    html_content += """
        </div>
        <div class="footer">
            <p>Generated by pipedoc - AI-powered DevOps agent</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write to file
    with open(output_path, "w") as f:
        f.write(html_content)
    
    return str(output_path)
