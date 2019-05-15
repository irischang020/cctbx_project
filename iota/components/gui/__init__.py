from __future__ import division, print_function, absolute_import

'''
Author      : Lyubimov, A.Y.
Created     : 04/02/2019
Last Changed: 04/02/2019
Description : IOTA GUI initialization module
'''

import sys

import wx

from libtbx import Auto
from libtbx.utils import Sorry, to_unicode, to_str

class IOTAPHILCtrl(object):
  """ Master class for all PHIL-compatible controls used in IOTA UI. Contains
      all the necessary functions for handling PHIL objects, so that GUI
      widgets can return PHIL strings and/or objects in a straightforward
      fashion """

  def __init__(self, phil_object):
    """ Constructor
    :param phil_object: PHIL object
    """

    assert phil_object is not None
    self.is_dlg_button = False
    self.is_definition = phil_object.is_definition
    self.is_scope = phil_object.is_scope
    self.full_path = phil_object.full_path()
    self.name = phil_object.name
    self.type = phil_object.type if phil_object.is_definition else 'scope'
    self.style = phil_object.style
    self.alias = phil_object.alias
    self.optional = phil_object.optional

    self.phil_string = phil_object.as_str()

    # None and Auto settings; this variable will determine if a blank entry (
    # e.g. a line of spaces) will cause an AutoType (True) or NoneType (
    # False) object to be returned by an IOTAPHILCtrl.
    self._blank_is_auto = False

    # Set expert level
    self.expert_level = phil_object.expert_level
    if self.expert_level is None:
      self.expert_level = 0


  def __str__(self):
    return type(self).__name__ + (" ({})".format(self.name))

  def SetUseAuto(self, enable=True):
    self._blank_is_auto = enable

  def UseAuto(self):
    return getattr(self, "_blank_is_auto", False)

  def ReturnNoneOrAuto(self, value=None):
    """ Return an AutoType object if value is Auto; returns a NonType object
        if value is None or blank (blank can be a string of spaces). If value
        is mistakenly not a blank, None, or Auto, this function will return a
        NoneType object """
    if str(value).replace(' ', '') == '':
      if self.IsOptional():
        if self.UseAuto():
          return Auto
        return None
      else :
        raise Sorry("Value required for {}.".format(self.GetName()))
    elif str(value).lower() == 'auto':
      return Auto
    elif str(value).lower() == 'none':
      return None
    else:
      return None

  def SetOptional(self, optional=True):
    if not optional:
      optional = True
    self.optional = optional

  def IsOptional(self):
    return getattr(self, "optional", True)

  def SetPHILName(self, name):
    self.name = name

  def GetPHILName(self):
    return getattr(self, "name", None)

  def GetPHIL(self):
    """ Override in subclasses with subclass-specific function """
    raise NotImplementedError()


class IOTADefinitionCtrl(IOTAPHILCtrl):
  """ Master class for all PHIL definition-compatible controls. """

  def __init__(self, phil_object):
    """ Constructor
    :param phil_object: PHIL definition object
    """
    IOTAPHILCtrl.__init__(self, phil_object=phil_object)
    assert phil_object.is_definition

  def GetPHIL(self, full_path=False, indent_length=2):
    """ Get PHIL entry for this control
    :param full_path: full object path, e.g. scope.sub_scope.definition
    :param indent_length: number of spaces per indent
    :return: if full_path=True, will return the full object path; otherwise,
    will return the object name, indented by indent_length * number of levels
    """
    assert self.name

    if full_path:
      return_string = self.full_path
    else :
      try:
        # Construct PHIL string from current value
        phil_name = self.full_path.split(".")[-1]
        value = self.GetStringValue()
        phil_string = '{} = {}'.format(phil_name, value)
      except Exception:
        # Use the default PHIL string
        phil_string = self.phil_string
      indent = len(self.full_path.split('.')) * indent_length
      return_string = '{:{ind}}{}'.format(' ', phil_string, ind=indent)

    return return_string

  def value_from_words(self, phil_object):
    """ Extract value, type, and whether value is None/Auto from PHIL object """
    value = phil_object.type.from_words(phil_object.words, phil_object)
    phil_type = phil_object.type.phil_type
    is_none_auto = (value is Auto or value is None)
    return value, phil_type, is_none_auto

  def GetStringValue(self):
    """ Override in subclasses with subclass-specific function """
    raise NotImplementedError()

  def SetValue(self, value):
    """ Overwrite in subclasses with subclass-specific function """
    raise NotImplementedError()


class IOTAScopeCtrl(IOTAPHILCtrl):
  """ Master class for all PHIL scope-compatible controls """

  def __init__(self, phil_object):
    """ Constructor
    :param phil_object: PHIL scope object
    """
    IOTAPHILCtrl.__init__(self, phil_object=phil_object)
    assert phil_object.is_scope

    self.controls = []
    # self.create_controls(scope=phil_object)

  def GetPHIL(self, path_only=False, indent_length=2):
    """ Get PHIL entry for this control
    :param path_only: return only the scope path (full path will be used)
    :param indent_length: number of spaces per indent
    :return: if path_only=True, return the scope path; else return the PHIL
    entry for the entire scope as a PHIL-formatted string
    """

    if path_only:
      phil_entries = [self.full_path]
    else:
      assert self.controls
      indent = len(self.full_path.split('.')) * indent_length
      phil_entries = self.add_scp_string(phil_ctrl=self, indent=indent,
                                         indent_length=indent_length)

      # print ('\n'.join(phil_entries))
    return phil_entries

  def add_scp_string(self, phil_ctrl, indent, indent_length):
    """ Recursively go through all controls in this scope control, extract
        their PHIL strings (or scopes) and create a list of PHIL strings
    :param phil_ctrl: a scope-type PHIL control object
    :param indent: total number of spaces by which to offset a PHIL string
    :param indent_length: number of spaces per indent 'tab'
    :return: list of PHIL strings
    """
    phil_strings = ['{:{ind}}{} {{'.format(' ', phil_ctrl.name, ind=indent)]
    end_point = '{:{ind}}}}'.format(' ', ind=indent)
    indent += indent_length

    for ctrl in phil_ctrl.controls:
      if ctrl.is_definition:
        dfn_string = self.add_dfn_string(ctrl, indent)
        phil_strings.append(dfn_string)
      elif ctrl.is_scope:
        scp_strings = ctrl.add_scp_string(ctrl, indent, indent_length)
        phil_strings.extend(scp_strings)
      elif ctrl.is_dlg_button:
        if ctrl.phil_strings:
          phil_strings.extend(ctrl.get_phil_strings())
        else:
          default_strings = ctrl.get_default_phil_strings()
          indented_strings = ["{:{ind}}{}".format('', s, ind=indent)
                              for s in default_strings]
          phil_strings.extend(indented_strings)
    phil_strings.append(end_point)
    return phil_strings

  def add_dfn_string(self, dfn, indent):
    """ Add a single PHIL string for a given definition control
    :param dfn: definition-type PHIL control
    :param indent: total number of spaces by which to offset a PHIL string
    :return: a single PHIL string
    """
    try:
      # Construct PHIL string from current value
      phil_name = dfn.name
      value = dfn.GetStringValue()
      phil_string = '{} = {}'.format(phil_name, value)
    except Exception:
      # Use the default PHIL string
      phil_string = dfn.phil_string.replace('\n', '')
    return_string = '{:{ind}}{}'.format(' ', phil_string, ind=indent)
    return return_string

  def _create_controls(self, scope):
    """ Create IOTA PHIL controls for a given scope (mainly for test
        purposes, as actual non-generic controls will be created by IOTA)
    :param scope: scope-type PHIL control
    """
    for obj in scope.active_objects():
      if obj.is_definition:
        self.controls.append(IOTADefinitionCtrl(obj))
      else:
        self.controls.append(IOTAScopeCtrl(obj))

class WidgetHandlerMixin(object):
  """ A mixin with sizer-specific widget-handling methods """

  def reset_layout(self):
    if isinstance(self, wx.Sizer):
      self.Layout()

  def HideAll(self):
    self.ShowItems(False)

  def ShowAll(self):
    self.ShowItems(True)

  def add_panel(self, panel, border=5):
    self.Add(panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=border)

  def add_widget(self, widget, border=5, expand=False, center=False):
    flags = wx.ALL | wx.ALIGN_CENTER_VERTICAL
    if expand:
      flags |= wx.EXPAND
    if center:
      flags |= wx.ALIGN_CENTER_HORIZONTAL
    self.Add(widget, 0, flags, border)

  def add_row_widget(self, widget, proportion=0, border=5):
    self.Add(widget, proportion, wx.LEFT | wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT,
             border)

  def add_expanding_widget(self, widget, proportion=0, border=5):
    self.Add(widget, proportion, wx.ALL | wx.EXPAND, border)

  def add_widgets(self,
                  widget_list,
                  flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
                  border=5):
    for widget in widget_list:
      self.Add(widget, 0, flag, border)

  def add_labeled_widget(self, widget, label, label_size=wx.DefaultSize,
                         *args,  **kwargs):
    self.label = wx.StaticText(self.parent, label=label, size=label_size)
    self.add_widget(widget=self.label)
    self.add_widget(widget=widget, *args, **kwargs)

  def __str__(self):
    return type(self).__module__ + "." + type(self).__name__

class TextCtrlValidator(wx.Validator):
  def __init__(self):
    wx.Validator.__init__(self)
    self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
    self.ctrl = None

  def Clone(self):
    return self.__class__()

  def TransferToWindow(self):
    return True

  def TransferFromWindow(self):
    return True

  def CheckFormat(self, value):
    return self.ctrl.CheckFormat(value)

  def Validate(self, parent):
    self.ctrl = self.GetWindow()
    try:
      value = to_unicode(self.ctrl.GetValue())
      if value:
        reformatted = self.CheckFormat(value)
        if isinstance(reformatted, str):
          reformatted = to_unicode(reformatted)
    except UnicodeEncodeError:
      self.ctrl.error_msg = "Only the standard UTF-8 character set is allowed."
      return False
    except Exception as e:
      self.ctrl.error_msg = str(e)
      return False
    else:
      self.ctrl.SetValue(value)
      return True

  def OnEnter(self, event):
    event.Skip()