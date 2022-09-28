from django.forms.widgets import TextInput


class ProgramRequirementsInput(TextInput):
    """
    This class implements a UI for program requirements
    """
    template_name = "forms/widgets/program-requirements-input.html"