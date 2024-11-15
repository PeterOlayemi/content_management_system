from administrator.models import Contact

def contact_info(request):
    contact = Contact.objects.first()  # Assuming you only have one instance
    return {'contact': contact}
