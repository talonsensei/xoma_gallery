import pdb

from django.http import HttpResponse

import xoma_gallery.files.models as files_m


def get_file(request, contents_pk):
  file_record = (files_m.FileRecord.objects.filter(_doc_contents=contents_pk) | \
    files_m.FileRecord.objects.filter(_img_contents=contents_pk))[0]
  response = HttpResponse(mimetype=str(file_record.mime_type))
  response.write(file_record.contents.read())
  return response