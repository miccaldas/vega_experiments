"""
Module Docstring
"""
import jinja2
import snoop
from dotenv import load_dotenv
from snoop import pp
import os


def type_watch(source, value):
    return f"type({source})", type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()


@snoop
def jinjatest():
    """"""
    jsons = os.getenv("JSONS")

    template_loader = jinja2.FileSystemLoader(searchpath="./templates/")
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "base.tpl"
    template = template_env.get_template(template_file)
    output_text = template.render(
        title="Test jina",
        description="This is a Jinja test.",
        page_url="http://localhost/vega_experiments/pages/test.html",
        graphic_title="Jinja Test",
        graph_width=800,
        data=f"{jsons}",
        xfield={"field": "hour", "type": "quantitative"},
    )
    html_path = "test.html"
    html_file = open(html_path, "w")
    html_file.write(output_text)
    html_file.close()


if __name__ == "__main__":
    jinjatest()
