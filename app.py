import time
from contacts_model import Contact, Archiver
import os

from flask import Flask, render_template, redirect, request, flash

app = Flask(__name__)


Contact.load_db()

# ========================================================
# Flask App
# ========================================================

# Set the secret key using an environment variable
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')


@app.route('/')
def index():
    return redirect("/contacts")


@app.route('/contacts')
def contacts():
    query = request.args.get('q', '')  # Get the search query

    if query:
        # Perform the search if a query is provided
        contacts_set = Contact.search(query)
    else:
        # Get all contacts if there's no query
        contacts_set = Contact.all()
        contacts_set = sorted(contacts_set, key=lambda c: c.first.lower())

    # If no contacts are found, just show the empty list without redirecting
    first_contact = contacts_set[0] if contacts_set else None

    # If no contacts are found, redirect to the "add new contact" page
    # if not contacts_set:
    #     return redirect('/contacts/new')

    # If the request comes from HTMX, return both the updated contact list and
    # the details panel
    if request.headers.get('HX-Request'):
        return render_template('_contact-list.html',
                               contacts=contacts_set,
                               query=query, contact=first_contact) + \
            render_template('_contact-details.html', contact=first_contact)

    # Pass the search query and the contacts to the template
    return render_template(
        'show.html',
        contacts=contacts_set,
        query=query,
        contact=first_contact
    )


@app.route('/contacts/')
def contacts_slash():
    return redirect("/contacts")


# GET: non-js route for new contact
@app.route("/contacts/new", methods=['GET'])
def contacts_new_get():
    all_contacts = Contact.all()  # Fetch all contacts for the left panel
    sorted_contacts = sorted(all_contacts, key=lambda c: c.first.lower())
    if request.headers.get('HX-Trigger') == 'button-add':
        return render_template("_form-add.html", contact=Contact(),
                               contacts=Contact.all())
    else:
        return render_template("new.html",
                               contact=Contact(),
                               contacts=sorted_contacts)
    # contacts=Contact.all())


# POST non-js: handle form submission
@app.route("/contacts/new", methods=['POST'])
def contacts_new():
    c = Contact(None, request.form['first_name'],
                request.form['last_name'],
                request.form['phone'],
                request.form['email'])

    all_contacts = Contact.all()
    sorted_contacts = sorted(all_contacts, key=lambda c: c.first.lower())

    if c.save():
        # Handle HTMX request
        if "HX-Request" in request.headers:
            return render_template("show.html", contact=c,
                                   contacts=sorted_contacts)
        else:
            # return redirect(f"/contacts/{contact_id}")
            return redirect("/contacts")
    else:
        return render_template("new.html", contact=c, contacts=sorted_contacts)


@app.route("/contacts/<contact_id>")
def contacts_view(contact_id=0):
    contact = Contact.find(contact_id)
    all_contacts = Contact.all()

    # Sort contacts alphabetically by first name
    # Use .lower() for case-insensitive sorting
    sorted_contacts = sorted(all_contacts, key=lambda c: c.first.lower())

    return render_template("show.html", contact=contact,
                           contacts=sorted_contacts)


@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id=0):
    contact = Contact.find(contact_id)
    all_contacts = Contact.all()  # Fetch all contacts for the left panel
    sorted_contacts = sorted(all_contacts, key=lambda c: c.first.lower())

    return render_template("edit.html", contact=contact,
                           contacts=sorted_contacts)


@app.route("/contacts/<contact_id>/edit", methods=["POST"])
def contacts_edit_post(contact_id=0):
    c = Contact.find(contact_id)
    all_contacts = Contact.all()  # Fetch all contacts for the left panel
    sorted_contacts = sorted(all_contacts, key=lambda c: c.first.lower())
    c.update(request.form['first_name'],
             request.form['last_name'],
             request.form['phone'],
             request.form['email'])

    if c.save():
        # Handle HTMX request
        if "HX-Request" in request.headers:
            # Redirect to the contact detail page after saving
            return redirect(f"/contacts/{contact_id}")
            # return render_template("show.html", contact=c,
            #                      contacts=sorted_contacts)
        else:
            return redirect(f"/contacts/{contact_id}")
    else:
        return render_template("edit.html", contact=c,
                               contacts=sorted_contacts)


# original REST route for DELETE
@app.route("/contacts/<contact_id>/delete", methods=["POST"])
def contacts_delete(contact_id=0):
    contact = Contact.find(contact_id)

    if contact is None:
        return "Contact not found", 404
    contact.delete()
    # flash("Deleted Contact!")
    return redirect("/contacts")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# AJAX ROUTES
# route for ajax delete
@app.route("/contacts/<contact_id>", methods=["DELETE"])
def contacts_delete_ajax(contact_id=0):
    contact = Contact.find(contact_id)

    if contact is None:
        return "Contact not found", 404

    # delete the contact
    contact.delete()

    # Fetch updated contact list
    sorted_contacts = sorted(Contact.all(), key=lambda c: c.first.lower())

    # Check if there's at least one contact left
    if sorted_contacts:
        # Select the first contact in the list after deletion
        first_contact = sorted_contacts[0]
        first_contact_id = first_contact.id
    else:
        first_contact = None  # No contacts available
        first_contact_id = None

    # Render both the updated contact list and the details of the first contact
    list_html = render_template(
        "_contact-list.html",
        contacts=sorted_contacts,
        contact=first_contact,
        active_id=first_contact_id)
    details_html = render_template(
        "_contact-details.html",
        contact=first_contact,
        active_id=first_contact_id)

    # Return both partials as separate HTML elements
    return f'''
        <div id="contacts-list" hx-swap-oob="true">{list_html}</div>
        <div id="details-panel" hx-swap-oob="true">
        {details_html if first_contact else "<p>No contact selected</p>"}</div>
    '''


# email validation route with ajax
@app.route("/contacts/<contact_id>/email", methods=["GET"])
def contacts_email_get(contact_id=0):
    c = Contact.find(contact_id)
    c.email = request.args.get('email')
    c.validate()
    return c.errors.get('email') or ""


@app.route('/ds')
def design_system():
    return render_template('ds/index.html')


if __name__ == '__main__':
    app.run(debug=True)
