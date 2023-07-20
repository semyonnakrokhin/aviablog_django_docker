from django import template

register = template.Library()

@register.simple_tag()
def track_images_html(form):
    field_collection = []
    for field_name in form.fields:
        if 'track_image_' in field_name:
            field_html = form[field_name]
            field_collection.append(field_html)

    return field_collection