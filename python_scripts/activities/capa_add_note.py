"""
capa_add_note - add a note about a capa
"""

from activities.activity_handler_class import ActivityHandler


class CapaAddNote(ActivityHandler):
    """
    Add a note about a capa

    :param capa_id: ID of the capa action 
    :param note_author: author of the note
    :param note_text: the note text

    :returns: An object containing the new activity's id 
    """

    required_args = {
        'capa_id',
        'note_author',
        'note_text'
    }
