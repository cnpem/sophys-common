.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :no-index:

   {% block attributes %}
   {% if attributes  %}
   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
   {% for item in (attributes | natural_sort) %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}
