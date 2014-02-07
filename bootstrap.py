
#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" bootstrap.py
    
    Usage:
        bootstrap.py -h
        bootstrap.py [-e] [<files>...]
        bootstrap.py [-t] [<theme-name>]

    Options:
        -h,--help       : show this help message
        -e,--exclude    : exclude files (one or more, coma separated)
        -t,--theme      : name of your custom theme that will be created

"""
# the above is our usage string that docopt will read and use to determine
# whether or not the user has passed valid arguments.

#Wordpress http://wordpress.org/latest.tar.gz Seems to be ratelimited :D 
#ACF http://downloads.wordpress.org/plugin/advanced-custom-fields.zip

from docopt import docopt
import sys, urllib2, fileinput
from subprocess import call
from src.classes import File


#Files to be downloaded (Only supports .zip, .js for now). Format: name, url, type
files = [   File('wordpress', 'http://oauthtest.agigen.se:13080/js/wordpress.zip', 'wordpress'),
            File('advanced-custom-fields', 'http://downloads.wordpress.org/plugin/advanced-custom-fields.zip', 'plugin'),
            File('jquery', 'http://code.jquery.com/jquery-1.11.0.js', 'jsfile')
        ]

#Settings
output_dir          = 'output'
files_dir           = 'files'
template_theme      = 'twentyfourteen'
default_theme_name  = 'mytheme'
require             = ['wget', 'unzip'] #Applications needed.

def main(docopt_args):
    """ main-entry point for program, expects dict with arguments from docopt() """
        
    # Notice, no checking for -h, or --help is written here.
    # docopt will automagically check for it and use your usage string.
    
    check_requirements()
    log('Launching you into the wordpress loop :D', colors['blue'] )
    # Get flags used
    if docopt_args["--exclude"] and docopt_args['<files>']:
        log('Excluding %s.' % docopt_args['<files>'], colors['blue'] )
        download_files( docopt_args )
    else:
        download_files( docopt_args )
    log('Done!', colors['green'] )

def download_files(docopt_args):
    exclude = docopt_args['<files>']
    ext = 'zip'
    for f in files:
        if f.name in exclude:
            continue
        log('Downloading %s' % f.name, colors['blue'] )
        if f.file_type == 'jsfile':
            ext = 'js'

        retcode = call(["wget", f.url , '-O', './%s/%s.%s' % (files_dir, f.name, ext) ])        
        if retcode < 0:
            log('Failed downloading %s' % f.name, colors['red'] )
            exit()
        else:
            log('Done downloading %s' % f.name, colors['green'] )

        unzip_file(f, docopt_args)

        #Create theme catalog.
        if f.file_type == 'wordpress':
            create_theme( str(docopt_args['<theme-name>']) )
    
    write_scripttags(docopt_args)

def unzip_file(f, docopt_args):
    log('Unzipping %s' % f.name, colors['blue'] )
    folder = files_dir    
    if f.file_type == 'wordpress':
        folder = output_dir
    if f.file_type == 'plugin':
        folder = '%s/wordpress/wp-content/plugins/' % output_dir
    if f.file_type == 'theme':
        folder = '%s/wordpress/wp-content/themes/' % output_dir
    if f.file_type == 'jszip':
        folder = '%s/wordpress/wp-content/themes/%s/js/' % (output_dir, theme_name(docopt_args) )
    if f.file_type == 'jsfile':
        #Dont unzip this. Just move it to js dir.
        call(['cp', '-R','%s/%s.js' % (files_dir, f.name), '%s/wordpress/wp-content/themes/%s/js/' % (output_dir,theme_name(docopt_args)) ])
        log('Copied jsfile %s to wordpress js directory.' % f.name, colors['green'] )
        return

    if call(['unzip', '%s/%s.zip' % (files_dir,f.name), '-d', folder ] ) < 0:
        log('Failed unzipping %s' % f.name, colors['red'] )
        quit()
    else:
        log('Done unzipping %s' % f.name, colors['green'] )

def create_theme(name=default_theme_name):
    log('Creating theme %s' % name, colors['blue'] )
    call(['cp', '-R', '%s/wordpress/wp-content/themes/%s' % (output_dir,template_theme), '%s/wordpress/wp-content/themes/%s' % (output_dir, name) ])

def write_scripttags(docopt_args):
    head_file = '%s/wordpress/wp-content/themes/%s/header.php' % (output_dir, theme_name(docopt_args)) #File that should be edited.

    header_trigger = '<?php wp_head(); ?>' #Insert stuff at this point in header.
    header_replacement = '' 

    bottom_body_trigger = ''  #Not implemented yet
    bottom_body_replacement = ''

    #Build a string for all js-files that should be included.
    for f in files:
        if f.file_type != 'jsfile':
            continue
        header_replacement += '<script src="<?php echo get_template_directory_uri(); ?>/js/%s.js"></script>\n' % f.name

    
    log('Adding script tags in file %s' % head_file, colors['blue'] )
    for i, line in enumerate(fileinput.input(head_file, inplace=1)):
        sys.stdout.write(line.replace(header_trigger, header_trigger + '\n'+ header_replacement ))  # replace header_trigger with header_replacement        

def theme_name(docopt_args):
    return str(docopt_args['<theme-name>']) if docopt_args['<theme-name>'] else default_theme_name

def log(text, color=''):
    print str(color) + str(text) + '\033[0m' #Last one is endcode.
def check_requirements():
    log('Checking requirements...', colors['blue'] )
    for r in require:
        try:
            call([r, '-q']) #Try quietly.
        except OSError as e:
            log('ERROR: Looks like you dont have %s :(' % r, colors['red'] )
            exit()
    log('Requirements OK.', colors['green'] )

 #Text output colors for your fancy terminal.
colors = {  'blue' : '\033[94m',
            'green': '\033[92m',
            'red'  : '\033[91m'
        }

# START OF SCRIPT
if __name__ == "__main__":
    # Docopt will check all arguments, and exit with the Usage string if they
    # don't pass.
    # If you simply want to pass your own modules documentation then use __doc__,
    # otherwise, you would pass another docopt-friendly usage string here.
    # You could also pass your own arguments instead of sys.argv with: docopt(__doc__, argv=[your, args])
    args = docopt(__doc__)

    # We have valid args, so run the program.
    main(args)