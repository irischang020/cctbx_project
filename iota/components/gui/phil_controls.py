from __future__ import division, print_function, absolute_import
from past.builtins import range

'''
Author      : Lyubimov, A.Y.
Created     : 04/02/2019
Last Changed: 04/02/2019
Description : IOTA GUI controls for PHIL-formatted settings
'''

import os
import sys
import wx
import wx.richtext
from wx.lib.agw.floatspin import FloatSpin

from wxtbx import bitmaps

from libtbx.utils import Sorry, to_unicode
from libtbx.phil import find_scope, parse

from iota.components import gui
from iota.components.gui import base
from iota.components.gui import controls as ct
from iota.components.iota_utils import InputFinder, makenone

ginp = InputFinder()

# Platform-specific stuff
# TODO: Will need to test this on Windows at some point
if wx.Platform == '__WXGTK__':
  norm_font_size = 10
  button_font_size = 12
  LABEL_SIZE = 14
  CAPTION_SIZE = 12
elif wx.Platform == '__WXMAC__':
  norm_font_size = 12
  button_font_size = 14
  LABEL_SIZE = 14
  CAPTION_SIZE = 12
elif (wx.Platform == '__WXMSW__'):
  norm_font_size = 9
  button_font_size = 11
  LABEL_SIZE = 11
  CAPTION_SIZE = 9

# Metallicbutton globals (temporary!)
GRADIENT_NORMAL = 0
GRADIENT_PRESSED = 1
GRADIENT_HIGHLIGHT = 2

MB_STYLE_DEFAULT = 1
MB_STYLE_BOLD_LABEL = 2
MB_STYLE_DROPARROW = 4

# -------------------------- PHIL Sizers and Panels -------------------------- #

class PHILSizer(wx.BoxSizer, gui.WidgetHandlerMixin):
  def __init__(self, parent, direction=wx.VERTICAL):
    super(PHILSizer, self).__init__(direction)
    self.parent = parent


class PHILBoxSizer(wx.StaticBoxSizer, gui.WidgetHandlerMixin):
  def __init__(self, parent, box, direction=wx.VERTICAL):
    super(PHILBoxSizer, self).__init__(box, direction)
    self.parent = parent

class PHILFlexGridSizer(wx.FlexGridSizer, gui.WidgetHandlerMixin):
  def __init__(self, parent, rows, cols, vgap, hgap):
    super(PHILFlexGridSizer, self).__init__(rows, cols, vgap, hgap)
    self.parent = parent
    self.label = None

  def add_growable(self, cols=None, rows=None, proportion=0):
    if cols:
      for col in cols:
        self.AddGrowableCol(idx=col, proportion=proportion)
    if rows:
      for row in rows:
        self.AddGrowableRow(idx=row, proportion=proportion)

class PHILBasePanel(base.ScrolledPanel, gui.IOTAScopeCtrl):
  def __init__(self, parent, scope, direction=wx.VERTICAL, box=True, label='',
               *args, **kwargs):
    base.ScrolledPanel.__init__(self, parent, *args, **kwargs)
    gui.IOTAScopeCtrl.__init__(self, scope)

    # Make scope panel
    if box:
      sz_box = wx.StaticBox(self, label=label)
      self.main_sizer = PHILBoxSizer(self, box=sz_box,
                                     direction=direction)
    else:
      self.main_sizer = PHILSizer(self, direction=direction)
    self.SetSizer(self.main_sizer)

    # Set expert level
    self.expert_level = scope.expert_level
    if self.expert_level is None:
      self.expert_level = 0

  def redraw_by_expert_level(self, expert_level=0):
    self.expert_level = expert_level
    self._show_hide_controls(controls=self.controls)

  def _show_hide_controls(self, controls):
    for ctrl in controls:
      if ctrl.expert_level > self.expert_level:
        ctrl.Hide()
      else:
        ctrl.Show()
        if ctrl.is_scope:
          self._show_hide_controls(ctrl.controls)


class PHILBaseScopePanel(wx.Panel, gui.IOTAScopeCtrl):
  def __init__(self, parent, scope, direction=wx.VERTICAL, box=True, label='',
               *args, **kwargs):
    wx.Panel.__init__(self, parent, *args, **kwargs)
    gui.IOTAScopeCtrl.__init__(self, scope)

    # Make scope panel
    if box:
      sz_box = wx.StaticBox(self, label=label)
      self.main_sizer = PHILBoxSizer(self, box=sz_box,
                                     direction=direction)
    else:
      self.main_sizer = PHILSizer(self, direction=direction)
    self.SetSizer(self.main_sizer)


class PHILBaseDefPanel(wx.Panel, gui.IOTADefinitionCtrl):
  """ Base class for the PHIL control, subclassed from wx.Panel and
      IOTADefinitionCtrl. The panel's main sizer is a FlexGridSizer, with a
      customizable grid depending on which kind of control is desired. """

  def __init__(self, parent, phil_object, rows=1, cols=2, vgap=10, hgap=10,
               label_size=wx.DefaultSize, *args, **kwargs):
    """ Constructor
    :param parent: parent object, typically another panel
    :param rows: Number of rows in the FlexGridSizer
    :param cols: Number of columns in the FlexGridSizer
    :param vgap: gap (in pixels) between rows (set to zero if rows=1)
    :param hgap: gap (in pixels) between columns (set to zero if cols=1)
    :param size: size of the panel
    """

    # Initialize wx.Panel attributes
    wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, *args, **kwargs)
    self.parent = parent
    self.error_btn = None
    self.ctr = None
    self.default_value = self.value_from_words(phil_object=phil_object)[0]

    # Initialize DefinitionCtrl attributes
    gui.IOTADefinitionCtrl.__init__(self, phil_object=phil_object)

    # Set grid
    vgap = vgap if rows > 1 else 0
    hgap = hgap if cols > 1 else 0
    self.ctrl_sizer = PHILFlexGridSizer(self, rows, cols+1, vgap, hgap)
    self.SetSizer(self.ctrl_sizer)

    # Attach and hide a small button that would show the format error message
    err_bmp = bitmaps.fetch_icon_bitmap('actions', 'status_unknown', size=16)
    self.error_btn = ct.GradButton(parent=self, bmp=err_bmp, button_margin=1,
                                   size=(22, 22), gradient_percent=0)
    self.ctrl_sizer.add_widget(self.error_btn)
    self.Bind(wx.EVT_BUTTON, self.ShowError, self.error_btn)
    self.error_btn.Hide()

  def GetLabelSize(self):
    size = self.ctrl_sizer.label.GetSize() if self.ctrl_sizer.label else (0, 0)
    return size

  def SetLabelSize(self, size=wx.DefaultSize):
    if self.ctrl_sizer.label:
      self.ctrl_sizer.label.SetSize(size)

  def GetStringValue(self):
    """ Override in subclasses with subclass-specific function """
    raise NotImplementedError()

  def SetValue(self, value):
    """ Overwrite in subclasses with subclass-specific function """
    raise NotImplementedError()

  def SetError(self, err):
    self.error_btn.user_data = err
    self.error_btn.Show()
    self.set_background(is_error=True)
    self.parent.Layout()
    self.Refresh()

  def RemoveError(self):
    self.error_btn.Hide()
    self.set_background(is_error=False)
    self.parent.Layout()
    self.Refresh()

  def ShowError(self, e):
    err = self.error_btn.user_data
    wx.MessageBox(caption='Format Error!',
                  message=str(err),
                  style=wx.ICON_EXCLAMATION|wx.STAY_ON_TOP)

  def set_background(self, is_error=False):
    c_err = (215, 48, 31)
    c_new = (254, 240, 217)

    if is_error:
      self.ctr.SetBackgroundColour(c_err)
    else:
      is_default = (self.ctr.GetValue() == str(self.default_value))
      if is_default:
        self.ctr.SetBackgroundColour(wx.NullColour)
      else:
        self.ctr.SetBackgroundColour(c_new)

  # def onToggle(self, e):
  #   """ Event handler for checkbox click
  #   :param e: event
  #   """
  #   self.toggle_boxes(flag_on=self.toggle.GetValue())
  #   e.Skip()
  #
  # def toggle_boxes(self, flag_on=True):
  #   """ Activate / deactivate child widgets depending on checkbox value
  #   :param flag_on: checkbox value
  #   """
  #   self.toggle.SetValue(flag_on)
  #
  #   if self.items is not None:
  #     if flag_on:
  #       for item in self.items:
  #         widget = self.__getattribute__(item[0])
  #         widget.Enable()
  #         value = widget.GetValue()
  #         if noneset(value) is None:
  #           widget.SetValue(str(item[1]))
  #         else:
  #           widget.SetValue(str(value))
  #     else:
  #       for item in self.items:
  #         widget = self.__getattribute__(item[0])
  #         widget.Disable()
  #         # widget.Clear()
  #
  # def reset_default(self):
  #   ''' Reset widget value to default '''
  #   if self.toggle is not None:
  #     self.toggle_boxes(flag_on=self.checkbox_state)
  #   else:
  #     for item in self.items:
  #       widget = self.__getattribute__(item[0])
  #       widget.Enable()
  #       widget.SetValue(item[1])


class PHILBaseDialog(base.FormattedDialog):
  """ Base dialog class for PHIL-formatted settings """
  def __init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE, *args, **kwargs):
    super(PHILBaseDialog, self).__init__(parent, style=style, *args, **kwargs)
    self.phil_sizer = PHILSizer(self)
    self.envelope.Add(self.phil_sizer, 1, flag=wx.EXPAND | wx.ALL, border=5)

# ------------------------------- PHIL Widgets ------------------------------- #

class ValidatedTextCtrl(wx.TextCtrl):
  ''' Base class for a wx.TextCtrl that performs PHIL-specific validation and
      format checking (sub-classes will customize those functions) '''

  def __init__(self, *args, **kwargs):
    self.error_msg = None

    # Intercept a specified value to be set after initialization
    saved_value = None
    if kwargs.get('value', "") != "":
      saved_value = kwargs['value']
      kwargs['value'] = ""

    # Initialize base class
    super(ValidatedTextCtrl, self).__init__(*args, **kwargs)
    self.parent = self.GetParent()

    # Set font style for text control
    font = wx.Font(norm_font_size, wx.FONTFAMILY_MODERN,
                   wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
    self.SetFont(font)
    style = self.GetWindowStyle()

    # Enforce "process ENTER" option
    if not style & wx.TE_PROCESS_ENTER:
      style |= wx.TE_PROCESS_ENTER
      self.SetWindowStyle(style)

    # Create appropriate validator (done in subclasses)
    self.SetValidator(self.CreateValidator())

    # Bindings
    self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self)
    self.Bind(wx.EVT_KILL_FOCUS, self.OnFocusLost, self)

    # Apply value if one was passed to control
    if saved_value is not None:
      if type(saved_value) == str:
        if saved_value.isspace():
          saved_value = self.parent.ReturnNoneOrAuto(value=saved_value)
        saved_value = to_unicode(saved_value)
      self.SetValue(saved_value)

  def Validate(self):
    is_good = self.GetValidator().Validate(parent=self.parent)
    if is_good:
      self.parent.RemoveError()
      self.Refresh()
    else:
      if not self.error_msg:
        self.error_msg = 'Unknown format error, please double-check your entry.'
      self.parent.SetError(self.error_msg)
      self.Refresh()

  def OnEnter(self, e=None):
    self.Validate()
    e.Skip()

  def OnFocusLost(self, e=None):
    self.Validate()
    e.Skip()

  def CreateValidator(self):
    return gui.TextCtrlValidator().Clone()


class ValidatedStringCtrl(ValidatedTextCtrl):
  def __init__(self, *args, **kwargs):
    super(ValidatedStringCtrl, self).__init__(*args, **kwargs)

    self._min_len = 0
    self._max_len = sys.maxint

  def SetMinLength(self, n):
    assert (n >= 0)
    self._min_len = n

  def SetMaxLength(self, n):
    assert (n >= 1)
    self._max_len = n

  def GetMinLength(self):
    return self._min_len

  def GetMaxLength(self):
    return self._max_len

  def CheckFormat(self, value):
    if "$" in value:
      raise ValueError("The dollar symbol ($) may not be used here.")
    elif len(value) > self.GetMaxLength():
      raise ValueError("Value must be {} characters or less."
                       "".format(self.GetMaxLength()))
    elif len(value) < self.GetMinLength():
      raise ValueError("Value must be at least {} characters."
                       "".format(self.GetMinLength()))
    return value


class ValidatedPathCtrl(ValidatedTextCtrl):
  def __init__(self, *args, **kwargs):
    super(ValidatedPathCtrl, self).__init__(*args, **kwargs)

    self.read = self.GetParent().read
    self.write = self.GetParent().write

  def CheckFormat(self, value=None):
    """ A hacky way to validate path syntax in a platform-independent way
    Args:
      value: path as string
    Returns: value if validated, raises ValueError if not
    """

    import errno

    # Just in case, check that entered path is string or unicode
    if not isinstance(value, str) and not isinstance(value, unicode):
      raise ValueError('Path must be a string!')

    # Check each path component for OS errors
    # Strip Windows-specific drive specifier (e.g., `C:\`) if it exists
    _, pathname = os.path.splitdrive(value)

    # Define directory guaranteed to exist
    root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
      if sys.platform == 'win32' else os.path.sep
    assert os.path.isdir(root_dirname)

    # Append a path separator to this directory if needed
    root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

    # Validate each path component
    for pathname_part in pathname.split(os.path.sep):
      try:
        os.lstat(root_dirname + pathname_part)
      except OSError as e:
        if hasattr(e, 'winerror'):
          if e.winerror == 123:
            raise ValueError("{} is not a valid Windows path!"
                             "".format(value))
        elif e.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
          raise ValueError("{} is not a valid Posix path!"
                           "".format(value))

    # Check permissions
    permission_errors = []
    if os.path.isdir(value):
      dirname = value
    else:
      dirname = os.path.dirname(value)
    if self.read and not os.access(dirname, os.R_OK):
      permission_errors.append('Read permission denied!')
    if self.write and not os.access(dirname, os.W_OK):
      permission_errors.append('Write permission denied!')
    if permission_errors:
      raise ValueError('Permission errors for {}:\n{}'
                       ''.format(dirname, '\n'.join(permission_errors)))
    return value


class ValidatedNumberCtrl(ValidatedTextCtrl):
  def __init__(self, *args, **kwargs):

    # Check for "type" kwarg, for int or float
    if kwargs.get(self, 'as_type'):
      self._num_type = kwargs.pop('as_type', None)
    else:
      self._num_type = 'float'  # float by default for now

    # Check for 'min' kwarg to set min value for control
    if kwargs.get(self, 'min'):
      min_num = kwargs.pop('min', None)
      if min_num is None:
        min_num = -sys.maxint
    else:
      min_num = -sys.maxint
    self._min_num = int(min_num) if self._num_type == 'int' else float(min_num)

    # Check for 'max' kwarg to set max value for control
    if kwargs.get(self, 'max'):
      max_num = kwargs.pop('max', None)
      if max_num is None:
        max_num = sys.maxint
    else:
      max_num = sys.maxint
    self._max_num = int(max_num) if self._num_type == 'int' else float(max_num)

    super(ValidatedNumberCtrl, self).__init__(*args, **kwargs)

  def SetMinValue(self, n):
    assert (n >= 0)
    self._min_num = n

  def SetMaxValue(self, n):
    assert (n >= 1)
    self._max_num = n

  def GetMinValue(self):
    return self._min_num

  def GetMaxValue(self):
    return self._max_num

  def CheckFormat(self, value):
    try:
      if self._num_type == 'int':
        value = int(value)
      elif self._num_type == 'float':
        value = float(value)
      else:
        value = float(value)
    except ValueError:
      value = str(value)

    is_none = self.parent.IsOptional()
    is_auto = self.parent.UseAuto()

    if isinstance(value, str):

      if value.lower() in ('none', 'auto') and (is_auto or is_none):
        pass         # allow None or Auto through the string filter
      else:
        if self._num_type == 'int':
          suggested_type = 'an integer'
        elif self._num_type == 'float':
          suggested_type = 'a float'
        else:
          suggested_type = 'a number'

        if is_auto and is_none:
          suggested_type += ', None, or Auto'
        elif is_none:
          suggested_type += 'or None'
        elif is_auto:
          suggested_type += ', None, or Auto'

        raise ValueError("String entries are not allowed! Enter {}, None, "
                         "or Auto.".format(suggested_type))
    else:
      if value > self.GetMaxValue():
        raise ValueError("Value ({}) must be less than the maximum of {}."
                         "".format(value, self.GetMaxValue()))
      elif value < self.GetMinValue():
        raise ValueError("Value ({}) must be more than the minimum of {}."
                         "".format(value, self.GetMinValue()))

    return value


class ValidatedUnitCellCtrl(ValidatedTextCtrl):
  def __init__(self, *args, **kwargs):
    super(ValidatedUnitCellCtrl, self).__init__(*args, **kwargs)

  def CheckFormat(self, value):
    """ Check that the entry is a valid unit cell notation
    Args:
      value: Unit cell parameters
    Returns: value if validated, raises ValueError if not
    """
    value = makenone(value)

    # Break up string by possible delimiters (set up to handle even a mixture
    # of delimiters, because you never know)
    if value:
      uc = value
      for dlm in [',', ';', '|', '-', '/']:
        if uc.count(dlm) > 0:
          uc = uc.replace(dlm, ' ')
      uc_params = uc.rsplit()

      error_msg = 'Invalid unit cell entry {}'.format(value)

      # Check if there are six parameters in unit cell (that's as far as
      # validation will go; the correctness of the unit cell is up to the user)
      if len(uc_params) != 6:
        raise ValueError('{}: should be six parameters!'.format(error_msg))

      # Check that every parameter can be converted to float (i.e. that the
      # parameters are actually all numbers)
      try:
        uc_params = [float(p) for p in uc_params]
      except ValueError as e:
        if 'invalid literal' in e.message.lower():
          raise ValueError('{}: unit cell should only contain '
                           'numbers'.format(error_msg))
        raise ValueError('{}: {}'.format(error_msg, e.message))

      uc = ' '.join(['{:.2f}'.format(p) for p in uc_params])

    else:
      uc = None

    return str(uc)


class ValidatedSpaceGroupCtrl(ValidatedTextCtrl):
  def __init__(self, *args, **kwargs):
    super(ValidatedSpaceGroupCtrl, self).__init__(*args, **kwargs)

  def CheckFormat(self, value):
    """ Check that the entry is a valid space group notation
    Args:
      value: Space group symbol and/or number
    Returns: value if validated, raises ValueError if not
    """

    # Attempt to create a space group object; if symbol or number are
    # invalid, this will fail
    from cctbx import crystal
    value = makenone(value)       # Convert to Nonetype if None or Null string

    if value:
      try:
        sym = crystal.symmetry(space_group_symbol=str(value))
      except RuntimeError as e:
        raise ValueError('Invalid space group entry:\n{}'.format(e))

      # Return space group symbol even if number is entered
      sg = sym.space_group_info()
    else:
      sg = None

    return str(sg)


# ------------------------------- PHIL Buttons ------------------------------- #

class PHILDialogButton(ct.IOTAButton):
  ''' Button that launches a wx.Dialog auto-populated with PHIL settings '''

  def __init__(self, parent, scope, selection=None, label=None,
               *args,  **kwargs):
    ct.IOTAButton.__init__(self, parent, *args, **kwargs)
    self.scope = scope
    self.selection = selection
    self.parent = parent
    self.name = scope.name
    self.phil_strings = None
    self.is_dlg_button = True
    self.is_scope = False
    self.is_definition = False
    self.expert_level = scope.expert_level if scope.expert_level else 0

    if label is None:
      label = scope.name.replace('_', ' ').capitalize() + "..."
    self.SetLabel(label)

  def get_phil_strings(self):
    return self.phil_strings

  def get_default_phil_strings(self):
    return self.scope.as_str().split('\n')

# ------------------------------ PHIL Controls ------------------------------- #

class PHILFileListCtrl(ct.FileListCtrl, gui.IOTADefinitionCtrl):
  def __init__(self, parent, phil_object):
    ct.FileListCtrl.__init__(self, parent=parent, size=(600, 300))
    gui.IOTADefinitionCtrl.__init__(self, phil_object=phil_object)


class PHILPathCtrl(PHILBaseDefPanel):
  """ Control for the PHIL path type """

  def __init__(self, parent, phil_object, label='', label_size=wx.DefaultSize,
               defaultfile='*', wildcard='*'):
    PHILBaseDefPanel.__init__(self, parent=parent, phil_object=phil_object,
                              label_size=label_size, cols=4, vgap=0)

    # Extract relevant styles
    phil_styles = phil_object.style.split(':') if phil_object.style else []
    if len(phil_styles) > 1:
      self.is_file = bool([('file' in i) for i in phil_styles])
      self.is_folder = bool([('folder' in i) for i in phil_styles])
      self.read = bool([('read' in i) for i in phil_styles])
      self.write = bool([('write' in i) for i in phil_styles])
    else:
      self.is_file = ('file' in phil_styles[0])
      self.is_folder = ('folder' in phil_styles[0])
      self.read = ('read' in phil_styles[0])
      self.write = ('write' in phil_styles[0])

    # If neither read-only nor write-only is specified, read/write is enabled
    if not self.read and not self.write:
      self.read = self.write = True

    # Set defaultfile and wildcard parameters for file dialog
    self.defaultfile = defaultfile
    self.wildcard = wildcard
    if self.is_file:
      bool_def = [('default' in i) for i in phil_styles]
      if bool(bool_def):
        def_card = phil_styles[bool_def.index(True)]
        self.defaultfile = def_card.split('=')[1]
      bool_wc  = [('wildcard' in i) for i in phil_styles]
      if bool(bool_wc):
        wc_card = phil_styles[bool_wc.index(True)]
        self.defaultfile = wc_card.split('=')[1]

    # Create path control
    self.ctr = ValidatedPathCtrl(self)
    self.SetStringValue(phil_object=phil_object)
    self.ctrl_sizer.add_labeled_widget(widget=self.ctr, label=label,
                                       expand=True, label_size=label_size)
    self.ctrl_sizer.add_growable(cols=[2])

    # Create browse and view buttons
    self.btn_browse = wx.Button(self, label='Browse...')
    viewmag_bmp = bitmaps.fetch_icon_bitmap('actions', 'viewmag', size=16)
    self.btn_mag = wx.BitmapButton(self, bitmap=viewmag_bmp)
    self.ctrl_sizer.add_widget(self.btn_browse)
    self.ctrl_sizer.add_widget(self.btn_mag)

    # Bindings
    self.Bind(wx.EVT_BUTTON, self.OnBrowse, self.btn_browse)

  def SetStringValue(self, phil_object):
    value = self.value_from_words(phil_object=phil_object)[0]
    self.ctr.SetValue(str(value))

  def GetStringValue(self):
    return self.ctr.GetValue()

  def OnBrowse(self, e):
    if self.is_file:
     self._open_file_dialog()
    elif self.is_folder:
      self._open_folder_dialog()
    else:
      command_list = [('Browse files...',
                       lambda evt: self._open_file_dialog()),
                      ('Browse folders...',
                       lambda evt: self._open_folder_dialog())]
      browse_menu = base.Menu(self)
      browse_menu.add_commands(command_list)
      self.PopupMenu(browse_menu)
      browse_menu.Destroy()

  def _open_folder_dialog(self):
    dlg = wx.DirDialog(self, "Choose folder:", style=wx.DD_DEFAULT_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
      self.ctr.SetValue(dlg.GetPath())
    dlg.Destroy()

  def _open_file_dialog(self):
    dlg = wx.FileDialog(
      self, message="Choose file",
      defaultDir=os.curdir,
      defaultFile=self.defaultfile,
      wildcard=self.wildcard,
      style=wx.FD_OPEN | wx.FD_CHANGE_DIR
    )
    if dlg.ShowModal() == wx.ID_OK:
      filepath = dlg.GetPaths()[0]
      self.ctr.SetValue(filepath)


class PHILStringCtrl(PHILBaseDefPanel):
  """ Control for the PHIL string type """

  def __init__(self, parent, phil_object, control=None,
               label='', label_size=wx.DefaultSize):
    PHILBaseDefPanel.__init__(self, parent=parent,
                              phil_object=phil_object,
                              label_size=label_size,
                              rows=1, cols=2, vgap=0, hgap=10)

    if not control:
      control = ValidatedStringCtrl

    self._create_control(control=control, phil_object=phil_object)
    self._place_control(label, label_size)

  def _create_control(self, control, phil_object):
    self.ctr = control(self)
    self.SetStringValue(phil_object=phil_object)

  def _place_control(self, label, label_size):
    self.ctrl_sizer.add_labeled_widget(widget=self.ctr, label=label,
                                       expand=True, label_size=label_size)
    self.ctrl_sizer.add_growable(cols=[2])

  def SetStringValue(self, phil_object):
    value = self.value_from_words(phil_object=phil_object)[0]
    if type(value) in (list, tuple):
      value = ' '.join(value)
    self.ctr.SetValue(str(value))

  def GetStringValue(self):
    return self.ctr.GetValue()


class PHILSpaceGroupCtrl(PHILStringCtrl):
  """ Control for the PHIL Space Group, subclassed from PHILStringCtrl """

  def __init__(self, parent, phil_object, label='', label_size=wx.DefaultSize):
    PHILStringCtrl.__init__(self, parent,
                            label=label,
                            control=ValidatedSpaceGroupCtrl,
                            phil_object=phil_object,
                            label_size=label_size)

class PHILUnitCellCtrl(PHILStringCtrl):
  """ Control for the PHIL Unit Cell, subclassed from PHILStringCtrl """

  def __init__(self, parent, phil_object, label='', label_size=wx.DefaultSize):
    PHILStringCtrl.__init__(self, parent,
                            phil_object=phil_object,
                            control=ValidatedUnitCellCtrl,
                            label=label,
                            label_size=label_size)


class PHILChoiceCtrl(PHILBaseDefPanel):
  """ Choice control for PHIL choice item, with label """

  def __init__(self, parent,
               phil_object,
               captions=None,
               label='',
               label_size=wx.DefaultSize,
               ctrl_size=wx.DefaultSize,
               allow_none=True,
               *args, **kwargs):
    """ Constructor
    :param parent: parent object
    :param choices: Choices in list or tuple format (a choice can contain an
    asterisk to designate selection; if that's the case, the choice control
    will be set to that selection)
    :param captions: Captions for selections (optional). The number of
    captions must be the same as the number of choices. Otherwise, choice
    names will serve as captions.
    :param label: choice control label
    :param label_size: size of choice control label
    :param label_style: normal, bold, italic, or italic_bold
    :param ctrl_size: size of choice control
    :param allow_none: allow for all the choices to be unselected (in that
    case, a three-dash entry will be added to the choice list, and the
    control set to that selection)
    """

    # Initialize the base class
    PHILBaseDefPanel.__init__(self, parent=parent, phil_object=phil_object,
                              label_size=label_size, *args, **kwargs)

    # Set choice control
    self.ctr = wx.Choice(self, size=ctrl_size)
    self.ctrl_sizer.add_labeled_widget(widget=self.ctr, label=label,
                                       label_size=label_size)

    # Set choices
    choices = [w.value for w in phil_object.words]
    self.SetChoices(choices=choices, captions=captions, allow_none=allow_none)

  def SetChoices(self, choices, captions=None, allow_none=True):
    ''' Insert choices into the control
    :param choices: list of choices (must be list or tuple)
    :param captions: list of captions (optional)
    :param allow_none: allow no selection
    '''

    # Determine selection
    selection = None
    is_selected = [("*" in choice) for choice in choices]
    if (True in is_selected):
      selection = is_selected.index(True)

    # Strip asterisk(s) from list of choices
    choices = [choice.replace("*", "") for choice in choices]

    # Apply or create captions and set selection
    if (captions is None):
      captions = list(choices)  # XXX force copy
    if (len(captions) != len(choices)):
      raise RuntimeError("Wrong number of caption items for '%s':\n%s\n%s" %
                         (self.GetName(), ";".join(choices),
                          ";".join(captions)))
    if (selection is None) and (allow_none):
      captions.insert(0, "---")
      choices.insert(0, None)
      selection = 0
    # not ideal, but changing "selection = None" to "selection = 0" can break
    # other choice widgets in other GUI panels
    if (selection is None) and not (allow_none):
      selection = 0
    self._options = choices
    self.ctr.SetItems(captions)
    self.ctr.SetSelection(selection)

  def SetValue(self, value):
    ''' Set choice selection to specific value '''
    if value not in self._options:
      raise Sorry('Value {} not found! Available choices are:\n{}'
                  ''.format(value, '\n'.join(self._options)))

    selection = self._options.index(value)
    self.ctr.SetSelection(selection)

  def GetValue(self):
    raise NotImplementedError("Please use GetPhilValue()")

  def GetPhilValue(self):
    """Returns a single string."""
    return self._options[self.ctr.GetSelection()]

  def GetStringValue(self):
    """Returns the long format (all choices, '*' denotes selected)."""
    selection = self.ctr.GetSelection()
    choices_out = []
    for i, choice in enumerate(self._options):
      if (choice is None):
        continue
      elif (i == selection):
        choices_out.append("*" + choice)
      else:
        choices_out.append(choice)
    return " ".join(choices_out)


class PHILNumberCtrl(PHILBaseDefPanel):
  """ Control for the PHIL int and float types """

  def __init__(self, parent, phil_object, label='', label_size=wx.DefaultSize):
    PHILBaseDefPanel.__init__(self, parent=parent, phil_object=phil_object,
                              rows=1, cols=2, vgap=0, hgap=10)


    self.ctr = ValidatedNumberCtrl(self,
                                   as_type=phil_object.type.phil_type,
                                   min=phil_object.type.value_min,
                                   max=phil_object.type.value_max)
    if hasattr(phil_object.type, 'allow_none_elements'):
      self.SetOptional(optional=phil_object.type.allow_none_elements)
    if hasattr(phil_object.type, 'allow_auto_elements'):
      self.SetUseAuto(enable=phil_object.type.allow_auto_elements)
    value = phil_object.type.from_words(phil_object.words, phil_object)

    self.ctr.SetValue(str(value))
    self.ctrl_sizer.add_labeled_widget(self.ctr, label=label,
                                       label_size=label_size, expand=True)
    self.ctrl_sizer.add_growable(cols=[1])

  def GetStringValue(self):
    """ Extract value as a string """
    return self.ctr.GetValue()


class PHILCheckBoxCtrl(PHILBaseDefPanel):
  """ Checkbox control for PHIL bool item """

  def __init__(self, parent, phil_object, label='', label_size=wx.DefaultSize):
    """ Constructor """
    PHILBaseDefPanel.__init__(self, parent=parent, phil_object=phil_object,
                              label_size=label_size, vgap=0)

    self.ctr = wx.CheckBox(self, label=label)
    self.ctrl_sizer.add_widget(widget=self.ctr)

  def GetStringValue(self):
    """ Extract value as a string """
    return str(self.ctr.GetValue())



class WidgetFactory(object):
  ''' Class that will automatically make widgets for automated dialog making '''
  w_kwargs = [
    'grid',
    'browse_btn',
    'mag_btn',
    'onChange',
    'onUpdate',
    'onToggle',
  ]

  widget_types = {
    'path'        : PHILPathCtrl     ,
    # 'input_list': PHILFileListCtrl ,
    'str'         : PHILStringCtrl   ,
    'choice'      : PHILChoiceCtrl   ,
    'number'      : PHILNumberCtrl   ,
    'bool'        : PHILCheckBoxCtrl,
    'space_group' : PHILSpaceGroupCtrl,
    'unit_cell'   : PHILUnitCellCtrl
  }

  def __init__(self):
    pass

  @staticmethod
  def make_widget(parent, phil_object, label_size=wx.DefaultSize,
                  widget_types=widget_types):

    wtype = phil_object.type.phil_type
    wstyle = phil_object.style
    wstyles = wstyle.split(':') if wstyle else []

    alias = phil_object.alias_path()
    if alias:
      label = alias
    else:
      label = phil_object.full_path().split('.')[-1]
      label = label.replace('_', ' ').capitalize()

    if wtype == 'bool:':
      label_size = wx.DefaultSize
    else:
      label += ": "

    if wtype in ('int', 'float'):
      wtype = 'number'

    if wtype == 'path' and 'input_list' in wstyles:
      widget = PHILFileListCtrl(parent=parent, phil_object=phil_object)
    else:
      if wtype in widget_types.keys():
        widget_ctrl = widget_types[wtype]
      else:
        widget_ctrl = PHILStringCtrl
      widget = widget_ctrl(parent=parent, phil_object=phil_object,
                           label=label, label_size=label_size)

    return widget

# ----------------------------- PHIL Controls -------------------------------- #

class PHILDialogPanel(PHILBasePanel):
  """ Factory class for dialog panel automatically created from PHIL
    settings """

  def __init__(self, parent, scope, *args, **kwargs):
    PHILBasePanel.__init__(self, parent=parent, scope=scope, box=False,
                           *args, **kwargs)

    for obj in scope.active_objects():
      if type(obj) in (list, tuple):
        pass
      else:
        max_label_size = self._get_max_label_size(scope=scope)
        if obj.is_scope:
          self.add_scope_box(obj=obj)
        elif obj.is_definition:
          self.add_definition_control(parent=self, obj=obj,
                                      label_size=max_label_size)
    self.redraw_by_expert_level()

  def _get_max_label_size(self, scope):
    # Get font info for string-to-pixels conversion
    panel_font = self.GetFont()
    dc = wx.WindowDC(self)
    dc.SetFont(panel_font)

    # Identify the longest label
    max_label_size = 0
    for o in scope.active_objects():
      if o.is_definition and o.type.phil_type != 'bool':
        alias = o.alias_path()
        label = alias if alias else o.full_path().split('.')[-1] + ': '
        label_size = dc.GetTextExtent(label)[0]
        if label_size > max_label_size:
          max_label_size = label_size

    # Pad max label size
    max_label_size += 5

    if max_label_size > 0:
      return wx.Size(max_label_size, -1)
    else:
      return wx.DefaultSize

  def get_all_path_names(self, phil_object, paths=None):
    if paths is None:
      paths = []
    if phil_object.is_scope:
      for obj in phil_object.objects:
        paths = self.get_all_path_names(obj, paths)
        paths.extend(paths)
    elif phil_object.is_definition:
      full_path = phil_object.full_path()
      if full_path not in paths:
        paths.append(full_path)
    return paths

  def add_definition_control(self, parent, obj, label_size=wx.DefaultSize):
    wdg = WidgetFactory.make_widget(parent, obj, label_size)
    if obj.type.phil_type in ('str', 'unit_cell', 'space_group', 'path'):
      expand = True
    else:
      expand = False
    parent.main_sizer.add_widget(widget=wdg, expand=expand)
    parent.controls.append(wdg)
    self.__setattr__(obj.name, wdg)

  def add_scope_box(self, obj):
    obj_name = obj.full_path().split('.')[-1]
    label = obj.alias_path() if obj.alias_path() else obj_name

    # Make scope panel
    panel = PHILBaseScopePanel(self, obj, box=True, label=label)
    panel_name = 'p_{}'.format(obj_name)
    self.__setattr__(panel_name, panel)

    self.main_sizer.Add(panel, flag=wx.ALL | wx.EXPAND, border=10)
    self.controls.append(panel)

    # Add widgets to box
    scope_objects = []
    max_label_size = self._get_max_label_size(obj)
    for box_obj in obj.active_objects():
      if box_obj.is_definition:
        self.add_definition_control(parent=panel, obj=box_obj,
                                    label_size = max_label_size)
      elif box_obj.is_scope:
        scope_objects.append(box_obj)

    # Add scope buttons to bottom of scope box
    self.add_scope_buttons(panel=panel, scopes=scope_objects)

  def add_scope_buttons(self, panel, scopes):
    btn_sizer = PHILSizer(parent=panel, direction=wx.HORIZONTAL)
    for scope in scopes:
      btn = PHILDialogButton(panel, scope,
                             handler_function=self.open_phil_dialog)
      panel.controls.append(btn)
      btn_sizer.add_widget(btn)
      self.__setattr__(btn.name, btn)
    panel.main_sizer.add_widget(btn_sizer, expand=True)

  def open_phil_dialog(self, e):
    btn = e.GetEventObject()
    title = btn.name.replace('_', ' ').capitalize()
    # phil_dlg = PHILDialog(btn.parent, scope=btn.scope, title=title)

    with PHILDialog(btn.parent, scope=btn.scope, selection=btn.selection,
                    title=title) as phil_dlg:
      if phil_dlg.ShowModal() == wx.ID_OK:
        btn.phil_strings = phil_dlg.phil_panel.GetPHIL()

  @classmethod
  def from_scope_objects(cls, parent, scope):

    scope_type = type(scope).__name__
    if scope_type in ('list', 'tuple'):
      objects = (r for r in scope)
    elif scope_type == 'scope':
      objects = scope.active_objects()
    else:
      objects = scope

    return cls(parent, objects)

  @classmethod
  def from_scope(cls, parent, scope):
    return cls(parent, scope)

  @classmethod
  def from_filename(cls, filepath):
    pass


class PHILDialog(PHILBaseDialog):
  ''' Dialog auto-populated with PHIL settings '''

  def __init__(self, parent, scope, selection=None, *args, **kwargs):
    dlg_style = wx.CAPTION | wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.STAY_ON_TOP
    super(PHILDialog, self).__init__(parent, style=dlg_style, *args, **kwargs)

    self.phil_strings = None

    if selection:
      scopes = []
      for sel in selection:
        scope = find_scope(scope, sel)
        if scope:
          scopes.append(scope)
        else:
          print ('PHIL ERROR: Scope "{}" not found!'.format(sel))

      self.scope = scope.customized_copy(objects=scopes)
    else:
      self.scope = scope

    self.phil_panel = PHILDialogPanel.from_scope(self, scope=self.scope)
    self.phil_sizer.add_panel(self.phil_panel)

    # Dialog control
    self.dlg_ctr = ct.DialogButtonsCtrl(self, preset='PHIL_DIALOG')
    self.envelope.Add(self.dlg_ctr,
                      flag=wx.EXPAND | wx.ALIGN_RIGHT | wx.ALL,
                      border=10)

    # Set up size and scrolling (adjust size if auto-fit dialog is too big
    # for screen)
    self.Fit()
    self.phil_panel.SetupScrolling()
    self._set_default_size(dialog_size=self.GetSize())
    self.Layout()

    # Bindings
    self.Bind(wx.EVT_BUTTON, self.OnOkay, id=wx.ID_OK)
    self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
    self.Bind(wx.EVT_CHOICE, self.OnExpertLevel, self.dlg_ctr.choice)

  def _set_default_size(self, dialog_size=wx.DefaultSize):
    # Get x, y of Display as well as of Dialog
    disp_idx = wx.Display.GetFromWindow(self.main_window)
    sw, sh = wx.Display(disp_idx).GetClientArea()[2:]
    dw, dh = dialog_size

    # Set dialog height (soft maximum to 2/3 of display height)
    soft_max_height = sh * (2/3)
    dlg_height = dh if dh <= soft_max_height else soft_max_height

    # Set dialog width (soft maximum to 1/3 of display width, pad if height
    # has been truncated, to accommodate the scroll bar)
    soft_max_width = sw / 3
    dw = dw + 20 if dlg_height < dh else dw
    dlg_width = dw if dw <= soft_max_width else soft_max_width

    # Apply size restrictions (wide enough to accommodate the button bar) and
    # set dialog size
    if sw > 500 and sh > 300:
      self.SetMinSize((500, 300))
    self.SetSize(wx.Size(dlg_width, dlg_height))

  def _collect_errors(self, panel=None):
    """ Go through all controls recursively and collect any format errors """

    if panel is None:
      panel = self.phil_panel

    errors = {}
    for ctrl in panel.controls:
      if ctrl.is_definition:
        if hasattr(ctrl.ctr, 'error_msg') and ctrl.ctr.error_msg:
          errors[ctrl.name] = ctrl.ctr.error_msg
      elif ctrl.is_scope:
        scope_errors = self._collect_errors(panel=ctrl)
        if scope_errors:
          errors.update(scope_errors)
      else:
        return None

    return errors

  def OnOkay (self, event):
    """ Check for saved errors and pop a warning if any are found (user
        cannot continue if any errors are present) """

    all_errors = self._collect_errors()
    if all_errors:
      # Check for errors and pop up a message if any are present
      wx.MessageBox(caption='Errors in Settings!',
                    message='Correct all errors to accept the changes.',
                    style=wx.OK|wx.ICON_EXCLAMATION)

    else:
      # Get formatted PHIL string, parse, and update the PHIL object
      self.phil_strings = self.phil_panel.GetPHIL()
      phil_string = '\n'.join(self.phil_strings)
      self.phil = parse(phil_string)
      self.EndModal(wx.ID_OK)

  def OnCancel (self, event):
    self.EndModal(wx.ID_CANCEL)

  def OnExpertLevel(self, event):
    expert_level = self.dlg_ctr.choice.GetSelection()
    self.phil_panel.redraw_by_expert_level(expert_level=expert_level)
    self.Layout()
    self.phil_panel.SetupScrolling()

