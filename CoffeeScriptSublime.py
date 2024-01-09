import sublime, sublime_plugin
from sublime import Region
import subprocess
import os
import json
import pathlib

def get_region_by_lines(line1, line2, view): 
  a = view.text_point(line1-1, 0) 
  lastCol = view.line(view.text_point(line2-1, 0)).b 
  return Region(a, lastCol)

def create_regions_template():
  return {
    "error": {
      "key": "groovy_error",
      "annotation_color": "red",
      "icon_color": "region.redish",
      "marks": [],
      "msgs": []
    },
    "info": {
      "key": "groovy_info",
      "annotation_color": "purple",
      "icon_color": "region.purplish",
      "marks": [],
      "msgs": []
    },
    "warning": {
      "key": "groovy_warning",
      "annotation_color": "orange",
      "icon_color": "region.orangish",
      "marks": [],
      "msgs": []
    }
  }   

def add_msgs_regions(lines, view):

  regions = create_regions_template()

  for it in regions:
    view.erase_regions(regions[it]["key"])


  for line in lines:
    msgs = lines[line]

    err_msg = filter(lambda it: it[0] == 'error', msgs)
    warn_msg = filter(lambda it: it[0] == 'warning', msgs)

    critical = list(err_msg) + list(warn_msg)
    
    [severity, msg] = next(iter(critical), msgs[0])


    [mark] = [get_region_by_lines(line, line, view)]

    if severity == "error":
      regions["error"]["marks"].append(mark)
      regions["error"]["msgs"].append(msg)
    elif severity == "warning":
      regions["warning"]["marks"].append(mark)
      regions["warning"]["msgs"].append(msg)
    elif severity == "info":
      regions["info"]["marks"].append(mark)
      regions["info"]["msgs"].append(msg)

        
  for r in regions:
    reg = regions[r]
    view.add_regions(reg["key"], 
      reg["marks"], 
      reg["icon_color"], 
      "dot", 
      sublime.HIDDEN | sublime.PERSISTENT, 
      annotations=reg["msgs"], 
      annotation_color=reg["annotation_color"])  

def run_linter(file, view):

    current = pathlib.Path(__file__).parent.resolve()

    cmd = ["coffeelint", 
           "--reporter", 
           "csv",
           "--file",
           "%s/coffeelint.json" % current,           
           file] 
    #print("cmd = %s" % " ".join(cmd))

    stdout, stderr = subprocess.Popen(
      [" ".join(cmd)],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      shell=True).communicate()

    if stderr.strip():
      print("CoffeeScriptLinter ERROR: %s" % stderr.strip().decode())

      r = stderr.decode('UTF-8')

      sublime.error_message("Coffee linter error: %s" % r)

    else:

   

      try:
        
        results = stdout.decode('UTF-8').strip().split("\n")
        lines = {}

        for result in results:

          parts = result.split(",")

          try:
            int(parts[1])
          except:
            continue

          line = int(parts[1])
          severity = parts[3]
          msg = parts[4]

          if line not in lines:
            lines[line] = []
          
          lines[line].append([severity, msg])

        add_msgs_regions(lines, view)

      except Exception as e:
        print("CoffeeScriptLinter fail: %s" % e)
        print("CoffeeScriptLinter ERROR: %s" % stderr.strip().decode())

class CoffeeFormatCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    region = sublime.Region(0, self.view.size())
    content = self.view.substr(region)
    fname = self.view.file_name()    
    
    self.view.erase_regions('mark')

    tmp_file = "/tmp/code.coffee"
    with open(tmp_file, 'w') as f:
        f.write(content)


    cmd = ["coffee-fmt", 
           "--indent_style=space", 
           "--indent_size=2",
           "-i",
           tmp_file] 
    #print("cmd = %s" % " ".join(cmd))

    sublime.status_message("Coffee format starting..")

    stdout, stderr = subprocess.Popen(
      [" ".join(cmd)],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      shell=True).communicate()

    if stderr.strip():
      print("CoffeeScriptFormat ERROR: %s" % stderr.strip().decode())

      r = stderr.decode('UTF-8')
      if 'Error formatting' in r:

        description = r.split("\n")
        if len(description) > 0:
          description = description[1].strip()
        else:
          description = r

        sublime.error_message("Coffee format error: %s" % description)

    else:


      run_linter(tmp_file, self.view)

      try:
        r = "%s\n" % stdout.decode('UTF-8').strip()

        if r.startswith('TypeError:') or r.startswith('Error:'):
          sublime.error_message("Coffee format error: %s" % r)
        else:
          self.view.replace(edit, region, r)
          sublime.status_message("Coffee format finished")
      except Exception as e:
        print("CoffeeScriptFormat fail: %s" % e)
        print("CoffeeScriptFormat ERROR: %s" % stderr.strip().decode())
        print("CoffeeScriptFormat RESULT: %s" % stdout.decode('UTF-8'))

def check_is_enabled_file(file_name):
  types = ['.coffee']

  for t in types:
    if file_name.lower().endswith(t):
      return True
  return False

class CoffeeEventDump(sublime_plugin.EventListener):


  def on_pre_save(self, view):
    if check_is_enabled_file(view.file_name()):
      view.run_command('coffee_format')


