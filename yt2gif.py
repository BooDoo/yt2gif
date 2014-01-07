import os, sys, argparse, httplib2
import pyimgur, cv2
import imgur as my_imgur
#import youtube_dl as yt
import youtube as yt
from CvVideo import CvVideo

parser = argparse.ArgumentParser(description='Make a GIF from a YouTube video clip')

req_group = parser.add_argument_group(title="Required")
req_group.add_argument('target', help='YouTube video id, or path to local file', metavar='VIDEO')

flags_group = parser.add_argument_group(title="Flags")
flags_group.add_argument('--hq', action='store_const', const=True, default=False, help='Download 720p instead of 360p video (default: False)')
flags_group.add_argument('--bw', action='store_const', const=True, default=False, help='Output as black + white (default: False)')
flags_group.add_argument('--cleanup', action='store_const', const=True, default=False, help='Delete source MP4 after GIF is made')

target_group = parser.add_argument_group(title="Target Time")
target_group.add_argument('-b', '--begin', '--start', type=float, default=0, help='Time to start at, in seconds (Default: 0)', metavar='#')
end_group = target_group.add_mutually_exclusive_group(required=True)
end_group.add_argument('-e', '--end', '--until', type=float, help='Time to end at, in seconds', metavar='#')
end_group.add_argument('-d', '--duration', '--length', type=float, help='Length of clip to make', metavar='#')

crop_group = parser.add_argument_group(title="Target Region of Interest")
roi_group = crop_group.add_mutually_exclusive_group()
roi_group.add_argument('-a', '--area', nargs=4, type=int, help='Use region (providing top-left/bottom-right)', metavar=('X0','Y0','X1','Y1'), dest='roi_rect')
roi_group.add_argument('-c', '--crop', nargs='+', help='Crop pixels or percent (top, right, bottom, left)', metavar='#[%]')

hsb_group = parser.add_argument_group(title="Hue/Saturation/Brightness")
hsb_group.add_argument('-m', '--modulate', '--hue', type=int, help='Modulate hue (see http://is.gd/HQlXTY) (Default: 100)', metavar = '#', dest='hue')
hsb_group.add_argument('-s', '--saturation', '--color', type=int, help='Saturation level (Default: 100)', metavar='%')
hsb_group.add_argument('-l', '--luminance', '--brightness', type=int, help='Brightness level (Default: 100)', metavar='%', dest='brightness')

misc_group = parser.add_argument_group(title="Misc Options")
misc_group.add_argument('-f', '--fps', '--framerate', type=int, help='Framerate of output GIF (default: no change)', metavar='#')
misc_group.add_argument('-z', '--fuzz', help='"Fuzz" factor for considering colors equivalent', default="4%", metavar="#%")
misc_group.add_argument('-p', '--pause', '--delay', type=int, help='Delay between frames (see http://is.gd/VePyHx)', metavar='#', dest='delay')
misc_group.add_argument('-o', '--outfile', '--filename', help='Output path/filename', metavar='PATH')
misc_group.add_argument('-u', '--upload', default='', help='Flag for upload to "imgur" or "tumblr" (environment variables required)', metavar='SERVICE')

#parser.add_argument('--resize', '-r', default=None, type=float, help='Resize output by scale factor')
#parser.add_argument('-m', '--max-size', '--limit' ...)
args = parser.parse_args()

#Open local file, or download and then open
args.outfile = args.outfile or (args.target + ".gif")

if os.path.isfile(args.target):
  vid_file = args.target
  vid = CvVideo(args.target, gif_path='', temp_path='', from_youtube=True)
else:
  vid_format = '22' if args.hq else '18'
  vid_file = (args.target + '-720.mp4') if args.hq else args.target + '.mp4'
  out_template = '%(id)s-720.%(ext)s' if args.hq else '%(id)s.%(ext)s'
  #yt_args = ['--restrict-filenames', '-f', vid_format, '-o', out_template, args.target]
  #yt.main(yt_args)
  yt.dl(dl_target=args.target, vid_format=vid_format, output=out_template)
  vid = CvVideo(vid_file, gif_path='', temp_path='', from_youtube=True)

#Determine ROI
if args.crop != None:
  if len(args.crop) > 3:
    #top, right, bottom, left
    top_crop, right_crop, bottom_crop, left_crop = args.crop
  elif len(args.crop) > 2:
    #top, left/right, bottom
    top_crop, right_crop, bottom_crop = args.crop
    left_crop = right_crop
  elif len(args.crop) > 1:
    #top/bottom, left/right
    top_crop, right_crop = args.crop
    bottom_crop = top_crop
    left_crop = right_crop
  elif len(args.crop) > 0:
    #all
    top_crop = right_crop = bottom_crop = left_crop = args.crop[0]

  if str(top_crop).endswith('%'):
    top_crop = float(top_crop[:-1]) / 100
    top_crop = round(vid.height * top_crop)
  if str(right_crop).endswith('%'):
    right_crop = float(right_crop[:-1]) / 100
    right_crop = round(vid.width * right_crop) 
  if str(bottom_crop).endswith('%'):
    bottom_crop = float(bottom_crop[:-1]) / 100
    bottom_crop = round(vid.height * bottom_crop)
  if str(left_crop).endswith('%'):
    left_crop = float(left_crop[:-1]) / 100
    left_crop = round(vid.width * left_crop)

  right_crop = vid.width - int(right_crop)
  bottom_crop = vid.height - int(bottom_crop)

  roi_rect = (int(left_crop), int(top_crop), int(right_crop), int(bottom_crop))

elif args.roi_rect != None:
  roi_rect = tuple([int(arg) for arg in args.roi_rect])

else:
  left_crop, top_crop, right_crop, bottom_crop = roi_rect = (0,0,vid.width,vid.height)

left_crop, top_crop, right_crop, bottom_crop = (int(left_crop), int(top_crop), int(right_crop), int(bottom_crop))

print '(min_x, min_y, max_x, max_y):', roi_rect
vid.crop_width = int(right_crop - left_crop)
vid.crop_height = int(bottom_crop - top_crop)

#Create output buffer of appropriate size
if args.fps:
  out_frame_skip = round(vid.fps / args.fps)
else:
  out_frame_skip = 1
gif_delay = args.delay or int(round(100.0 / (vid.fps / out_frame_skip)))
fps = args.fps or vid.fps
#vid.output = cv2.VideoWriter(vid.out_avi,0,int(fps),(vid.crop_width,vid.crop_height))
vid.reset_output(0,fps)

#Output clip to output file
from_frame = round(args.begin * vid.fps)
if args.end:
  to_frame = round(args.end * vid.fps)
elif args.duration:
  to_frame = round(args.duration * vid.fps) + from_frame

vid.clip_to_output(
  from_frame=from_frame,
  to_frame=to_frame,
  frame_skip=out_frame_skip,
  use_roi=True,
  roi_rect=roi_rect
)

#Make a GIF
args.fuzz = args.fuzz if str(args.fuzz).endswith('%') else str(args.fuzz) + '%'
args.delay = args.delay or args.fps
vid.gif_from_out_avi(
  out_file=args.outfile,
  color=not args.bw,
  brightness=args.brightness or 100,
  saturation= args.saturation or 100,
  hue=args.hue or 100,
  delay=gif_delay,
  fuzz=args.fuzz
)

#portability hack
try:
    WindowsError
except NameError:
    WindowsError = None

try:
  if args.cleanup:
    os.remove(os.path.join(vid_file))
  vid.clear_out_avi()
except (WindowsError, IOError) as e:
  print "\n\nWasn't able to remove video files. DO IT YOURSELF.\n"
  #print e

#Upload it?
if args.upload.lower() == 'imgur':
  try:
    #Assign some custom utility functions to pyimgur module:
    pyimgur.init_with_refresh = my_imgur.imgur_init_with_refresh
    pyimgur.Imgur.manual_auth = my_imgur.imgur_manual_auth
    IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET, IMGUR_ALBUM_ID, IMGUR_REFRESH_TOKEN = [os.getenv(line.rstrip()) for line in open('imgur_secrets','r')]
    imgur = pyimgur.init_with_refresh(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET, IMGUR_REFRESH_TOKEN)
    imgur.refresh_access_token()
  except pyimgur.requests.exceptions.ConnectionError as e:
    imgur = None
    print 'No internet?'
    raise e

if args.upload.lower() == 'tumblr':
  try:
    TUMBLR_CONSUMER_KEY, TUMBLR_CONSUMER_SECRET, TUMBLR_OAUTH_TOKEN, TUMBLR_OAUTH_SECRET, TUMBLR_BLOG_NAME = [os.getenv(line.rstrip()) for line in open('tumblr_secrets','r')]
    tumblr = pytumblr.TumblrRestClient(
      TUMBLR_CONSUMER_KEY,
      TUMBLR_CONSUMER_SECRET,
      TUMBLR_OAUTH_TOKEN,
      TUMBLR_OAUTH_SECRET
    )
  except httplib2.ServerNotFoundError as e:
    tumblr = None
    print 'No internet?'
    raise e
