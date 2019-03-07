
# TODO:
#  - cached scenes

from __future__ import division
from libtbx.math_utils import roundoff
from cctbx.miller import display
from websocket_server import WebsocketServer
import threading, math
from time import sleep
import os.path
import libtbx
import webbrowser, tempfile



class hklview_3d:
  def __init__ (self, *args, **kwds) :
    self.settings = kwds.get("settings")
    self.buffer_factor = 2.0
    self.min_slab = 4
    self.min_viewport_use_fraction = 0.1
    self.min_dist = 4.0
    self.flag_show_fog = True
    self.flag_use_lights = True
    self.flag_use_quadrics = False
    self.miller_array = None
    self.d_min = None
    self.scene = None
    self.animation_time = 0
    self.NGLscriptstr = ""
    self.cameratype = "orthographic"
    self.colbinname = ""
    self.binvals = []
    self.maxdata = 0.0
    self.mindata = 0.0
    self.nbin = 0
    self.websockclient = None
    self.StartWebsocket()
    tempdir = tempfile.gettempdir()
    self.hklfname = os.path.join(tempdir, "hkl.htm" )
    if os.path.isfile(self.hklfname):
      os.remove(self.hklfname)
    self.jscriptfname = os.path.join(tempdir, "hkljstr.js")
    if os.path.isfile(self.jscriptfname):
      os.remove(self.jscriptfname)
    self.hklhtml = r"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">

<html>
<head>
<meta charset="utf-8" />
</head>

<body>
<script src="%s" type="text/javascript"></script>

<script src="%s" type="text/javascript"></script>
    """
    self.htmldiv = """
<div id="viewport" style="width:100\%; height:100\%;"></div>

</body></html>

    """


  def __exit__(self, exc_type, exc_value, traceback):
    # not called unless instantiated with a "with hklview_3d ... " statement
    self.server.shutdown()
    if os.path.isfile(self.hklfname):
      os.remove(self.hklfname)


  def set_miller_array (self, miller_array, merge=None, details="") :
    if (miller_array is None) : return
    self.miller_array = miller_array
    self.merge = merge
    self.d_min = miller_array.d_min()
    array_info = miller_array.info()
    uc = "a=%g b=%g c=%g angles=%g,%g,%g" % miller_array.unit_cell().parameters()
    print "Data: %s %s, %d reflections in space group: %s, unit Cell: %s" \
      % (array_info.label_string(), details, miller_array.indices().size(),
          miller_array.space_group_info(), uc)
    self.construct_reciprocal_space(merge=merge)


  def construct_reciprocal_space (self, merge=None) :
    self.scene = display.scene(miller_array=self.miller_array,
      merge=merge,
      settings=self.settings)
    self.rotation_center = (0,0,0)
    self.maxdata = max(self.scene.data)
    self.mindata = min(self.scene.data)
    print "Min, max values: %f, %f" %(self.mindata , self.maxdata)


  def DrawNGLJavaScript(self):
    if self.miller_array is None :
      print "A miller array must be selected for drawing"
      return

    h_axis = self.scene.axes[0]
    k_axis = self.scene.axes[1]
    l_axis = self.scene.axes[2]
    nrefls = self.scene.points.size()

    Hstararrowstart = roundoff( [-h_axis[0]*100, -h_axis[1]*100, -h_axis[2]*100] )
    Hstararrowend = roundoff( [h_axis[0]*100, h_axis[1]*100, h_axis[2]*100] )
    Hstararrowtxt  = roundoff( [h_axis[0]*102, h_axis[1]*102, h_axis[2]*102] )
    Kstararrowstart = roundoff( [-k_axis[0]*100, -k_axis[1]*100, -k_axis[2]*100] )
    Kstararrowend = roundoff( [k_axis[0]*100, k_axis[1]*100, k_axis[2]*100] )
    Kstararrowtxt  = roundoff( [k_axis[0]*102, k_axis[1]*102, k_axis[2]*102] )
    Lstararrowstart = roundoff( [-l_axis[0]*100, -l_axis[1]*100, -l_axis[2]*100] )
    Lstararrowend = roundoff( [l_axis[0]*100, l_axis[1]*100, l_axis[2]*100] )
    Lstararrowtxt  = roundoff( [l_axis[0]*102, l_axis[1]*102, l_axis[2]*102] )

    arrowstr = """
    // xyz arrows
    shape.addSphere( [0,0,0] , [ 1, 1, 1 ], 0.3, 'Origo');
    //blue-x
    shape.addArrow( %s, %s , [ 0, 0, 1 ], 0.1);
    //green-y
    shape.addArrow( %s, %s , [ 0, 1, 0 ], 0.1);
    //red-z
    shape.addArrow( %s, %s , [ 1, 0, 0 ], 0.1);

    shape.addText( %s, [ 0, 0, 1 ], 5, 'H');
    shape.addText( %s, [ 0, 1, 0 ], 5, 'K');
    shape.addText( %s, [ 1, 0, 0 ], 5, 'L');
    """ %(str(Hstararrowstart), str(Hstararrowend), str(Kstararrowstart), str(Kstararrowend),
          str(Lstararrowstart), str(Lstararrowend), Hstararrowtxt, Kstararrowtxt, Lstararrowtxt)

    colors = self.scene.colors
    radii = self.scene.radii * self.settings.scale
    points = self.scene.points
    data = self.scene.data
    hkls = self.scene.indices
    dres = self.scene.work_array.d_spacings().data()
    colstr = self.scene.miller_array.info().label_string()
    assert (colors.size() == radii.size() == nrefls)
    shapespherestr = ""
    shapespherestr2 = ""
    shapespherestr3 = ""
    shapespherestr4 = ""
    shapespherestr5 = ""
    colours = []
    positions = []
    radii2 = []
    spbufttips = []

    if len(self.binvals) <1:
      self.binvals.append(min(data))
      self.binvals.append(max(data))
    self.nbin = len(self.binvals)

    for ibin in range(self.nbin):
      colours.append([])
      positions.append([])
      radii2.append([])
      spbufttips.append([])

    def data2bin(d):
      for ibin, binval in enumerate(self.binvals):
        if (ibin+1) == self.nbin:
          return ibin
        if d > binval and d <= self.binvals[ibin+1]:
          return ibin
      raise Sorry("Should never get here")

    for i, hklstars in enumerate(points):
      ibin = data2bin( data[i] )
      spbufttip = "H,K,L: %s, %s, %s" %(hkls[i][0], hkls[i][1], hkls[i][2])
      spbufttip += "\ndres: %s" %str(roundoff(dres[i])  )
      spbufttip += "\n%s: %s" %(colstr, str(roundoff(data[i]) ) )
      #import code, traceback; code.interact(local=locals(), banner="".join( traceback.format_stack(limit=10) ) )
      positions[ibin].extend( roundoff(list(hklstars)) )
      colours[ibin].extend( roundoff(list(colors[i]), 2) )
      radii2[ibin].append( roundoff(radii[i], 2) )
      spbufttips[ibin].append(spbufttip)

    spherebufferstr = """
  ttips = new Array(%d)
  positions = new Array(%d)
  colours = new Array(%d)
  radii = new Array(%d)
  spherebufs = new Array(%d)
    """ %(self.nbin, self.nbin, self.nbin, self.nbin, self.nbin)

    for ibin in range(self.nbin):
      nreflsinbin = len(radii2[ibin])
      if (ibin+1) < self.nbin:
        print "%d reflections with %s in ]%2.2f; %2.2f]" %(nreflsinbin, colstr,
                                        self.binvals[ibin], self.binvals[ibin+1])
      if nreflsinbin > 0:
        spherebufferstr += """
  // %d spheres
  ttips[%d] = %s
  positions[%d] = new Float32Array( %s )
  colours[%d] = new Float32Array( %s )
  radii[%d] = new Float32Array( %s )
  spherebufs[%d] = new NGL.SphereBuffer({
    position: positions[%d],
    color: colours[%d],
    radius: radii[%d],
    picking: ttips[%d],
  })
  shape.addBuffer(spherebufs[%d])
      """ %(nreflsinbin, ibin, str(spbufttips[ibin]), ibin, str(positions[ibin]),
      ibin, str(colours[ibin]), ibin, str(radii2[ibin]),
      ibin, ibin, ibin, ibin, ibin, ibin )

    spherebufferstr += """
// create tooltip element and add to the viewer canvas
  tooltip = document.createElement("div");
  Object.assign(tooltip.style, {
    display: "none",
    position: "absolute",
    zIndex: 10,
    pointerEvents: "none",
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    color: "lightgrey",
    padding: "0.5em",
    fontFamily: "sans-serif"
  });

  stage.viewer.container.appendChild(tooltip);
  // listen to `hovered` signal to move tooltip around and change its text
  stage.signals.hovered.add(function (pickingProxy) {
    if (pickingProxy && (Object.prototype.toString.call(pickingProxy.picker) === '[object Array]'  )){
      var sphere = pickingProxy.sphere;
      var cp = pickingProxy.canvasPosition;
      tooltip.innerText = pickingProxy.picker[pickingProxy.pid];
      tooltip.style.bottom = cp.y + 3 + "px";
      tooltip.style.left = cp.x + 3 + "px";
      tooltip.style.display = "block";
    }else{
      tooltip.style.display = "none";
    }
  });

  stage.signals.clicked.add(function (pickingProxy) {
  if (pickingProxy && (Object.prototype.toString.call(pickingProxy.picker) === '[object Array]'  )){
    var innerText = pickingProxy.picker[pickingProxy.pid];
    mysocket.send( innerText);
  }
  });

    """

    self.NGLscriptstr = """
// Microsoft Edge users follow instructions on
// https://stackoverflow.com/questions/31772564/websocket-to-localhost-not-working-on-microsoft-edge
// to enable websocket connection

var mysocket = new WebSocket('ws://127.0.0.1:7894/');

mysocket.onopen = function () {
  mysocket.send('%s now connected via websocket');
};

// Log errors to debugger of your browser
mysocket.onerror = function (error) {
  console.log('WebSocket Error ' + error);
};


window.addEventListener( 'resize', function( event ){
    stage.handleResize();
}, false );


var stage;
var shape;
var shapeComp;
var repr;

var hklscene = function (b) {
  shape = new NGL.Shape('shape');
  stage = new NGL.Stage('viewport', { backgroundColor: "grey", tooltip:false });
  stage.setParameters( { cameraType: "%s" } );

  %s

  %s

  shapeComp = stage.addComponentFromObject(shape);
  repr = shapeComp.addRepresentation('buffer');
  shapeComp.autoView();
  repr.update()
}

document.addEventListener('DOMContentLoaded', function() { hklscene() }, false );


mysocket.onmessage = function (e) {
  //alert('Server: ' + e.data);
  var c
  var alpha
  var si
  mysocket.send('got ' + e.data ); // tell server what it sent us
  try {
    val = e.data.split(",")
    var ibin = parseInt(val[1])

    if (val[0] === "alpha") {
      alpha = parseFloat(val[2])
      spherebufs[ibin].setParameters({opacity: alpha})
      stage.viewer.requestRender()
    }

    if (val[0] === "colour") {
      si =  parseInt(val[2])
      colours[ibin][3*si] = parseFloat(val[3])
      colours[ibin][3*si+1] = parseFloat(val[4])
      colours[ibin][3*si+2] = parseFloat(val[5])
      spherebufs[ibin].setAttributes({ color: colours[ibin] })
      stage.viewer.requestRender()
    }

    if (val[0] === "Redraw") {
      stage.viewer.requestRender()
    }

    if (val[0] === "Reload") {
    // refresh browser with the javascript file
      window.location.reload(true);
    }

  }
  catch(err) {
    mysocket.send('error: ' + err );
  }
};




    """ % (self.__module__, self.cameratype, arrowstr, spherebufferstr)
    if self.jscriptfname:
      with open( self.jscriptfname, "w") as f:
        f.write( self.NGLscriptstr )
    self.ReloadNGL()


  #--- user input and settings
  def update_settings (self) :
    self.construct_reciprocal_space(merge=self.merge)
    self.DrawNGLJavaScript()
    msg = "Rendered %d reflections\n" % self.scene.points.size()
    return msg


  def process_pick_points (self) :
    self.closest_point_i_seq = None
    if (self.pick_points is not None) and (self.scene is not None) :
      closest_point_i_seq = gltbx.viewer_utils.closest_visible_point(
        points=self.scene.points,
        atoms_visible=self.scene.visible_points,
        point0=self.pick_points[0],
        point1=self.pick_points[1])
      if (closest_point_i_seq is not None) :
        self.closest_point_i_seq = closest_point_i_seq
    if (self.closest_point_i_seq is not None) :
      self.scene.label_points.add(self.closest_point_i_seq)
      self.GetParent().update_clicked(index=self.closest_point_i_seq)
      #hkl, d_min, value = self.scene.get_reflection_info(
      #  self.closest_point_i_seq)
      #self.GetParent().update_clicked(hkl, d_min, value)
    else :
      self.GetParent().update_clicked(index=None)


  def OnConnectWebsocketClient(self, client, server):
    self.websockclient = client
    print "got a new client:", self.websockclient


  def OnWebsocketClientMessage(self, client, server, message):
    if message != "":
      print message


  def StartWebsocket(self):
    self.server = WebsocketServer(7894, host='127.0.0.1')
    self.server.set_fn_new_client(self.OnConnectWebsocketClient)
    self.server.set_fn_message_received(self.OnWebsocketClientMessage)
    self.wst = threading.Thread(target=self.server.run_forever)
    self.wst.daemon = True
    self.wst.start()


  def SendWebSockMsg(self, msg):
    if self.websockclient:
      self.server.send_message(self.websockclient, msg )
    else:
      self.OpenBrowser()


  def SetOpacity(self, bin, alpha):
    if bin > self.nbin:
      print "There are only %d bins of data present" %self.nbin
      return
    msg = u"alpha, %d, %f" %(bin, alpha)
    self.SendWebSockMsg(msg)


  def RedrawNGL(self):
    self.SendWebSockMsg( u"Redraw, NGL" )


  def ReloadNGL(self): # expensive as javascript may be several Mbytes large
    self.SendWebSockMsg( u"Reload, NGL" )


  def OpenBrowser(self):
    NGLlibpath = os.path.join( libtbx.env.under_dist("crys3d", "hklview"), "ngl.js")
    htmlstr = self.hklhtml %(NGLlibpath, self.jscriptfname)
    htmlstr += self.htmldiv
    with open(self.hklfname, "w") as f:
      f.write( htmlstr )
    url = "file:///" + self.hklfname
    print "Writing %s and connecting to its websocket client" %self.hklfname
    webbrowser.open(url, new=1)




"""
# python2 code

from websocket_server import WebsocketServer
import threading, math
from time import sleep

nc = {}
def new_client(client, server):
  nc = client
  print "got a new client:", nc

def on_message(client, server, message):
    print message

websocket.enableTrace(True)
server = WebsocketServer(7894, host='127.0.0.1')
server.set_fn_new_client(new_client)
server.set_fn_message_received(on_message)

wst = threading.Thread(target=server.run_forever)
wst.daemon = True
wst.start()

def LoopSendMessages():
  x = 0.0
  i=0
  while server.clients:
    nc = server.clients[0]
    x += 0.2
    alpha =  (math.cos(x) +1.0 )/2.0
    msg = u"alpha, 2, %f" %alpha
    server.send_message(server.clients[0], msg )
    r = (math.cos(x) +1.0 )/2.0
    g = (math.cos(x+1) +1.0 )/2.0
    b = (math.cos(x+2) +1.0 )/2.0
    msg = u"colour, 1, %d, %f, %f, %f" %(i,r,g,b)
    server.send_message(server.clients[0], msg )
    sleep(0.2)



"""


"""

# python3 code


import asyncio
import datetime
import math
import websockets

async def time(websocket, path):
  x = 0
  for i in range(1000):
    x += 0.2
    alpha =  (math.cos(x) +1.0 )/2.0
    msg = u"alpha, 2, %f" %alpha
    await websocket.send( msg )
    r = (math.cos(x) +1.0 )/2.0
    g = (math.cos(x+1) +1.0 )/2.0
    b = (math.cos(x+2) +1.0 )/2.0
    msg = u"colour, 1, %d, %f, %f, %f" %(i,r,g,b)
    await websocket.send( msg )
    message = await websocket.recv()
    print( message)
    await asyncio.sleep(0.2)

start_server = websockets.serve(time, '127.0.0.1', 7894)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()



"""





