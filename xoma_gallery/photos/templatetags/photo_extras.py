import pdb

from django import template

import photos.models as photos_m

register = template.Library()

class IsScoredNode(template.Node):
  def __init__(self, entry_id, voter_id):
    self.entry_id = template.Variable(entry_id)
    self.voter_id = template.Variable(voter_id)

  def render(self, context):
    if bool(photos_m.Vote.objects.filter(
        voter=self.voter_id.resolve(context), entry=self.entry_id.resolve(context)).count()):
      return "On"
    else:
      return "Off"

class EntryScoreNode(template.Node):
  def __init__(self, entry_id, voter_id):
    self.entry_id = template.Variable(entry_id)
    self.voter_id = template.Variable(voter_id)

  def render(self, context):
    try:
      vote = photos_m.Vote.objects.get(
          voter=self.voter_id.resolve(context), entry=self.entry_id.resolve(context))
      return vote.score
    except photos_m.Vote.DoesNotExist:
      pass

@register.tag
def entry_scored_by_voter(parser, token):
  try:
    # split_contents() knows not to split quoted strings.
    tag_name, entry_id, voter_id = token.split_contents()
  except ValueError:
    raise template.TemplateSyntaxError, ("%r tag requires exactly two arguments" %
        token.contents.split()[0])      
  return IsScoredNode(entry_id, voter_id)

@register.tag
def entry_score(parser, token):
  """docstring for entry_score"""
  try:
    # split_contents() knows not to split quoted strings.
    tag_name, entry_id, voter_id = token.split_contents()
  except ValueError:
    raise template.TemplateSyntaxError, ("%r tag requires exactly two arguments" %
        token.contents.split()[0])      
  return EntryScoreNode(entry_id, voter_id)