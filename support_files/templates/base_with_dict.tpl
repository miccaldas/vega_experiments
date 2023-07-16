<!DOCTYPE html>
<html>
    <head>
    <title>{{ title }}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="Mclds">
    <meta name="description" content="{{ description }}">
    <meta property="og:type" content="web page">
    <meta property="og:url" content="{{ page_url }}">
    <script src="https://cdn.jsdelivr.net/npm/vega@5.25.0"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@5.9.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@6.22.1"></script>
    <link rel="stylesheet" type="text/css" href="http://localhost/{{ project }}/css/index.css" media="screen">
    <style media="screen">
      /* Add space between Vega-Embed links  */
      .vega-actions a {
        margin-right: 5px;
      }
    </style>
    </head>
    <body>
    <div id="vis">
    </div>
    <h1>{{ graphic_title }}</h1>
   <script>
            // Assign the specification to a local variable vlSpec.
            var vlSpec = {
            $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
            width: {{ width }},
            {% if height %}
            height: {{ height }},
            {% endif %}
            data: {
            {% if dictdata +%}
            values: [ 
                {% for i in dictdata %}
                {{ i }},
                {% endfor %} 
            {% endif %}
                ]
            },
            mark: {{ mark }},
            {% if config %}
            config: {{ config }},
            {% endif %}
            encoding: {
                x: {{ xfield }},
                {% if yfield %}
                y: {{ yfield }},
                {% endif %}
                {% if color %}
                color: {{ color }},
                {% endif %}
            }
            };
            vegaEmbed('#vis', vlSpec);
        </script>
         </body>
</html>


