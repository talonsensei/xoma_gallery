# Create your views here.
import re
import pdb
import random

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.simple import redirect_to
from django.template import RequestContext

import decider.models as dec_m


def decision(request):
  """starting page for this application"""
  options = dec_m.Option.objects.all()
  decision = options[random.randint(0, len(options) - 1)]
  return render_to_response(
      'decision.html', {'decision': decision, 'options': options},
      context_instance=RequestContext(request))
      
