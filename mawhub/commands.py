
from pathlib import Path
import click
from frappe.commands import pass_context


@click.command('sql-gen')
@click.option('--site', required=True, help='Site Name to connect to')
@click.option('--prefix', required=True , help='prefix that used to get all table to generate')
@click.option('--output-file', required=True , help='output destintation')
@pass_context
def sql_gen(_context, site : str, prefix:str,output_file:str):
    """Execute custom database query"""
    import frappe
    frappe.init(site=site)
        # 2. Connect to the database
    frappe.connect()
    try:
        from mawhub.pkg.sql.sql_generator import (
            sql_generate_by_prefix,
        )

        out = sql_generate_by_prefix(prefix=prefix,output_file=output_file)
        click.echo(f"✔ TAL SQL types generated → {out}")

    except Exception as e:
        click.echo(f"Error executing query: {str(e)}")

commands = [sql_gen]



@click.command('sql-gen-tables')
@click.option('--site', required=True, help='Site Name to connect to')
@click.option('--tables', required=True , help='prefix that used to get all table to generate')
@click.option('--output-file', required=True , help='output destintation')
@pass_context
def sql_gen_tables(_context, site : str, tables:str,output_file:str):
    """Execute custom database query"""
    import frappe
    frappe.init(site=site)
        # 2. Connect to the database
    frappe.connect()
    try:
        from mawhub.pkg.sql.sql_generator import (
            sql_generate_by_table_names,
        )

        out = sql_generate_by_table_names(table_names=tables.split(','),output_file=output_file)
        click.echo(f"✔ TAL SQL types generated → {out}")

    except Exception as e:
        click.echo(f"Error executing query: {str(e)}")

@click.command('api-gen')
@click.option('--input', '-i', required=True, help='Python API file')
@click.option('--output', '-o', required=True, help='Output TS file')
@click.option('--app', default='mawhub', help='Frappe app name')
@pass_context
def api_gen(_context, input: str, output: str, app: str):
    """Generates TS createResource wrappers for Whitelisted functions"""
    from mawhub.pkg.tsgenerator.tsgenerator_utils import generate_api_resources

    in_p = Path(input).expanduser()
    out_p = Path(output).expanduser()

    content = generate_api_resources(in_p, app)

    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(content, encoding="utf-8")
    click.secho(f"✔ API Resources generated → {out_p}", fg="green")


commands = [sql_gen,sql_gen_tables,api_gen]
