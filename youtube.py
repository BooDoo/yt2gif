import subprocess, urllib2, json, os.path, sys

def dl(dl_target=None, vid_format='18', vid_path=None, output=None, queue_file=None, rate_limit=None):
  #subprocess.call(['youtube-dl', '--restrict-filenames', '-f', vid_format, '-o', os.path.join(vid_path, '%(uploader)s___%(id)s.%(ext)s'), '--download-archive', dl_log_file, '--rate-limit', rate_limit, '--max-downloads', str(max_downloads), '-a', queue_file])
  call_args = ['youtube-dl', '--restrict-filenames']
  try:
    output = os.path.join(vid_path, output)
  except (TypeError, AttributeError) as e:
    pass

  if output:
    call_args.extend(['-o', output])
  else:
    call_args.extend(['-o', '%(id)s.%(ext)s'])

  if vid_format:
    call_args.extend(['-f', str(vid_format)])
  if rate_limit:
    call_args.extend(['--rate-limit', rate_limit])

  if queue_file:
    call_args.extend(['-a', queue_file])
  elif dl_target:
    call_args.append(dl_target)
  #Now call it:
  #print " ".join(call_args)
  subprocess.call(call_args)
