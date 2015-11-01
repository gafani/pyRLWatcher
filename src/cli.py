import click


@click.command()
@click.option('--debug', '-d', is_flag=True,  help='debug mode')
@click.option('--service', '-s', is_flag=True, help='run service')
@click.argument('path')
def cli(debug, service, path):
    click.echo(debug)
    click.echo(service)
    click.echo(path)


if __name__ == '__main__':
    cli()
