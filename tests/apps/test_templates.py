from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import TestCase


class TemplateBlockTests(TestCase):
    """Test cases for template block functionality, particularly the HTML block."""

    def test_html_block_default(self):
        """Test that the default HTML block renders <html> without modifications."""
        # Create a simple template that extends base.html without overriding the html block
        template_string = """
        {% extends "allauth/layouts/base.html" %}
        {% block content %}Test Content{% endblock %}
        """

        # Render the template
        template = Template(template_string)
        rendered = template.render(Context({}))

        # Verify the default <html> tag is present
        self.assertIn("<html>", rendered)
        self.assertNotIn("data-theme", rendered)

    def test_html_block_override(self):
        """Test that the HTML block can be overridden with custom attributes."""
        # Create a template that overrides the html block
        template_string = """
        {% extends "allauth/layouts/base.html" %}
        {% block html %}<html data-theme="dark" lang="en">{% endblock %}
        {% block content %}Test Content{% endblock %}
        """

        # Render the template
        template = Template(template_string)
        rendered = template.render(Context({}))

        # Verify custom attributes are present
        self.assertIn('<html data-theme="dark" lang="en">', rendered)
        self.assertIn("Test Content", rendered)

    def test_html_block_with_data_theme(self):
        """Test the specific use case of adding a data-theme attribute."""
        # Create a template with data-theme attribute
        template_string = """
        {% extends "allauth/layouts/base.html" %}
        {% block html %}<html data-theme="custom-theme">{% endblock %}
        {% block content %}Themed Content{% endblock %}
        """

        # Render the template
        template = Template(template_string)
        rendered = template.render(Context({}))

        # Verify data-theme attribute is present
        self.assertIn('data-theme="custom-theme"', rendered)
        self.assertIn("Themed Content", rendered)

    def test_html_block_multiple_attributes(self):
        """Test the HTML block with multiple custom attributes."""
        # Create a template with multiple attributes
        template_string = """
        {% extends "allauth/layouts/base.html" %}
        {% block html %}<html data-theme="light" lang="fr" dir="ltr" class="no-js">{% endblock %}
        {% block content %}Multi-attribute Content{% endblock %}
        """

        # Render the template
        template = Template(template_string)
        rendered = template.render(Context({}))

        # Verify all attributes are present
        self.assertIn('data-theme="light"', rendered)
        self.assertIn('lang="fr"', rendered)
        self.assertIn('dir="ltr"', rendered)
        self.assertIn('class="no-js"', rendered)
        self.assertIn("Multi-attribute Content", rendered)

    def test_html_block_backward_compatibility(self):
        """Test that templates not using the HTML block continue to work."""
        # Test a simple template that doesn't override the html block
        template_string = """
        {% extends "allauth/layouts/base.html" %}
        {% block head_title %}Test Title{% endblock %}
        {% block content %}Legacy Content{% endblock %}
        """

        # Render the template
        template = Template(template_string)
        rendered = template.render(Context({}))

        # Verify basic structure is intact
        self.assertIn("<html>", rendered)
        self.assertIn("Test Title", rendered)
        self.assertIn("Legacy Content", rendered)
        # Ensure no unexpected attributes were added
        self.assertNotIn("data-", rendered)

    def test_base_template_renders_correctly(self):
        """Test that the base template renders correctly with the HTML block."""
        # Directly render the base template
        rendered = render_to_string("allauth/layouts/base.html", {})

        # Verify the HTML structure is correct
        self.assertIn("<!DOCTYPE html>", rendered)
        self.assertIn("<html>", rendered)
        self.assertIn("</html>", rendered)
        self.assertIn("<head>", rendered)
        self.assertIn("</head>", rendered)
        self.assertIn("<body>", rendered)
        self.assertIn("</body>", rendered)
