import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Shell from 'gi://Shell';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as Background from 'resource:///org/gnome/shell/ui/background.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
export default class Render extends Extension {
 enable() {
  this.timer=GLib.timeout_add(GLib.PRIORITY_DEFAULT,2500,()=>{
   this.timer=0;
   try {
    this.widget=new St.Widget({x:0,y:0,width:Number(GLib.getenv('BLUR_WIDTH')),height:Number(GLib.getenv('BLUR_HEIGHT')),effect:new Shell.BlurEffect({name:'blur',radius:Number(GLib.getenv('BLUR_RADIUS')),brightness:Number(GLib.getenv('BLUR_BRIGHTNESS'))})});
    this.manager=new Background.BackgroundManager({container:this.widget,monitorIndex:0,controlPosition:false});
    Main.uiGroup.add_child(this.widget);
    this.timer=GLib.timeout_add(GLib.PRIORITY_DEFAULT,2000,()=>{
     this.timer=0;
     try {
      const stream=Gio.File.new_for_path(GLib.getenv('BLUR_OUTPUT')).replace(null,false,Gio.FileCreateFlags.NONE,null);
      this.screenshot=new Shell.Screenshot();
      this.screenshot.screenshot(false,stream,(obj,result)=>{
       try {
        obj.screenshot_finish(result);stream.close(null);this.report('PASS');
       }catch(e){this.report('FAIL '+e.stack);}
      });
     }catch(e){this.report('FAIL '+e.stack);}
     return GLib.SOURCE_REMOVE;
    });
   }catch(e){this.report('FAIL '+e.stack);}
   return GLib.SOURCE_REMOVE;
  });
 }
 report(message){Gio.File.new_for_path(GLib.getenv('BLUR_REPORT')).replace_contents(message,null,false,Gio.FileCreateFlags.NONE,null);}
 disable(){if(this.timer)GLib.source_remove(this.timer);this.manager?.destroy();this.widget?.destroy();}
}
