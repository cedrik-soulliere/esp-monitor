from ._anvil_designer import FrameTemplate
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ..Capteurs import Capteurs
from ..Parametre import Parametre
from ..Logout import Logout
from datetime import datetime

class Frame(FrameTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    #Present users with a login form with just one line of code:
    #anvil.users.login_with_form()

    anvil.users.login_with_form()
    print(f"This user has logged in: {anvil.users.get_user()['email']}")

    #Set the Plotly plots template to match the theme of the app
    Plot.templates.default = "material_light"
    #When the app starts up, the Sales form will be added to the page
    self.content_panel.add_component(Capteurs())
    #Change the role of the sales_page_link to look selected
    self.sales_page_link.role = "selected"
    self.date_label.text = datetime.today().strftime("%B %d, %Y")


  def sales_page_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    #Clear the content panel and add the Sales Form
    self.content_panel.clear()
    self.content_panel.add_component(Capteurs())
    #Make the sales_page_link look selected and deselect the reports_page_link
    self.sales_page_link.role = "selected"
    self.reports_page_link.role = "default"



  def reports_page_link_click(self, **event_args):
      """This method is called when the link is clicked"""
      # Clear the content panel and add the Parametre form
      self.content_panel.clear()

      from ..Parametre import Parametre   # Lazy import to avoid circular import
      self.content_panel.add_component(Parametre())

      # Make the reports_page_link look selected and deselect the sales_page_link
      self.reports_page_link.role = "selected"
      self.sales_page_link.role = "default"

#If using the Users service, uncomment this code to log out the user:

  def signout_link_click(self, **event_args):
    #  """This method is called when the link is clicked"""
    anvil.users.logout()
    open_form('Logout')
