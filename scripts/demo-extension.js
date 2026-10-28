import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';
import Shell from 'gi://Shell';
import Clutter from 'gi://Clutter';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
const wait=ms=>new Promise(resolve=>GLib.timeout_add(GLib.PRIORITY_DEFAULT,ms,()=>{resolve();return GLib.SOURCE_REMOVE;}));
export default class Demo extends Extension {
 enable(){this.run().catch(error=>this.report('FAIL '+error+'\n'+error.stack));}
 async shot(name,caption){
  this.caption.text=caption;await wait(450);
  const file=Gio.File.new_for_path(GLib.getenv('DEMO_OUTPUT')+'/'+name+'.png');
  const stream=file.replace(null,false,Gio.FileCreateFlags.NONE,null);
  const screenshot=new Shell.Screenshot();
  await new Promise((resolve,reject)=>screenshot.screenshot(false,stream,(object,result)=>{try{object.screenshot_finish(result);stream.close(null);resolve();}catch(error){reject(error);}}));
 }
 async run(){
  await wait(2800);Main.overview.hide();await wait(700);
  this.caption=new St.Label({text:'',style:'font-size: 24px; color: white; background-color: #151922; padding: 22px; border-radius: 14px;',x:40,y:40});
  Main.uiGroup.add_child(this.caption);
  const ext=Main.extensionManager.lookup('zorin-menu@zorinos.com');
  const menu=ext.stateObj.menuButtons[0]._menu;
  menu.open();await wait(400);
  const favorites=menu._layout._appsSection._favorites;
  favorites._settings.set_strv('apps',['org.gnome.Terminal.desktop','org.gnome.Calculator.desktop']);favorites._settings.apply();
  await wait(1400);
  const sanitize=actor=>{if(actor instanceof St.Label)actor.text='Usuario de prueba';for(const child of actor.get_children())sanitize(child);};
  sanitize(menu._layout._userButton);
  const avatar=menu._layout._userButton?._avatar;
  if(avatar){avatar.set_style('');avatar.set_child(new St.Icon({icon_name:'avatar-default-symbolic',icon_size:28}));}
  await this.shot('01-menu-favoritos','Menú de inicio: favoritos propios arriba; todas las aplicaciones debajo');
  const button=menu._layout._appsSection._favoriteWidgets[1].get_children()[0];
  button.popupMenu();await this.shot('02-menu-clic-derecho','Clic derecho: agregar o quitar favoritos solo del inicio');button._menu?.close();menu.close();
  const bar=global.zorinTaskbar.panels[0].taskbar;const c=bar._compactFavorites;
  this.pointer=Clutter.get_default_backend().get_default_seat().create_virtual_device(Clutter.InputDeviceType.POINTER_DEVICE);
  this.pointer.notify_absolute_motion(GLib.get_monotonic_time(),1000,200);await wait(900);
  this.child=Gio.Subprocess.new(['/usr/bin/gjs',GLib.getenv('DEMO_WINDOW')],Gio.SubprocessFlags.NONE);
  for(let i=0;i<30 && !global.get_window_actors().length;i++)await wait(200);
  if(!global.get_window_actors().length)throw Error('No apareció la ventana de prueba');
  await wait(800);
  await this.shot('03-barra-solo-abiertas','Sin hover: solo las aplicaciones con ventanas abiertas');
  const [px,py]=c.panel.get_transformed_position();const [w,h]=c.panel.get_transformed_size();
  this.pointer.notify_absolute_motion(GLib.get_monotonic_time(),px+w*0.65,py+h*0.5);await wait(1400);
  if(!c._idleRevealed)throw Error('No se activó el hover en espacio vacío');
  await this.shot('04-barra-favoritos','Hover sobre un espacio vacío: favoritos en la misma barra, a tamaño completo');
  this.pointer.notify_absolute_motion(GLib.get_monotonic_time(),1000,200);await wait(1000);
  const date=bar.dtpPanel.allocationMap.dateMenu.actor;
  const [dx,dy]=date.get_transformed_position();const [dw,dh]=date.get_transformed_size();
  this.pointer.notify_absolute_motion(GLib.get_monotonic_time(),dx+dw/2,dy+dh/2);await wait(900);
  if(c._idleRevealed)throw Error('El reloj activó los favoritos');
  await this.shot('05-barra-zonas-excluidas','El reloj y los indicadores no activan la aparición de favoritos');
  this.report('PASS: screenshots captured with isolated preferences and neutral demo applications.');
 }
 report(message){Gio.File.new_for_path(GLib.getenv('DEMO_REPORT')).replace_contents(message,null,false,Gio.FileCreateFlags.NONE,null);}
 disable(){this.child?.force_exit();this.caption?.destroy();}
}
