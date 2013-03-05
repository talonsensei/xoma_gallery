import re
import pdb

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.simple import redirect_to
from django.template import RequestContext

import xoma_gallery.photos.models as photos_m


def index(request):
  """starting page for this application"""
  contests = photos_m.Contest.objects.all()
  return render_to_response(
      'index.html', {'contests': contests}, context_instance=RequestContext(request))

      
def show_contest(request, contest_id):
  contest = get_object_or_404(photos_m.Contest, pk=contest_id)
  categories = {}
  for cat in contest.categories.all():
    categories[cat.name] = []
    for entry in cat.entries.all():
      if not request.user.is_anonymous():
        try:
          vote = entry.votes.get(voter=request.user)
          entry.voted = True
          entry.score = vote.score
        except photos_m.Vote.DoesNotExist:
          pass
      categories[cat.name].append(entry)
  
  return render_to_response(
      'show_contest.html', {'contest': contest, 'categories': categories}, 
      context_instance=RequestContext(request))

      
def show_results(request, contest_id):
  contest = get_object_or_404(photos_m.Contest, pk=contest_id)
  return render_to_response(
      'show_results.html', {'contest': contest}, context_instance=RequestContext(request))


def rate(request, entry_id):
  """docstring for vote"""
  entry = get_object_or_404(photos_m.Entry, pk=entry_id)
  rating = pk=request.POST['rating']
  pdb.set_trace()
  photos_m.Vote.objects.get_or_create(entry=entry, voter=request.user, defaults={'score':rating})
  return HttpResponse('it worked')