imports.gi.versions.Gtk = '3.0';
const {Gtk,Gdk,GLib}=imports.gi;
GLib.set_prgname('org.codex.DesktopDemo');
Gdk.set_program_class('org.codex.DesktopDemo');
Gtk.init(null);
const window=new Gtk.Window({title:'Ventana de demostración',default_width:620,default_height:300});
window.set_wmclass('org.codex.DesktopDemo','org.codex.DesktopDemo');
window.add(new Gtk.Label({label:'Esta ventana pertenece a la sesión de prueba.\nNo contiene datos personales.'}));
window.connect('destroy',()=>Gtk.main_quit());window.show_all();Gtk.main();
