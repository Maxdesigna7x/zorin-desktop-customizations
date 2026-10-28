import Clutter from 'gi://Clutter'
import GLib from 'gi://GLib'
import St from 'gi://St'
export class CompactFavorites {
  constructor(taskbar) {
    this.taskbar = taskbar
    this.panel = taskbar.dtpPanel.panel
    this._idleRevealed = false
    this._openItemMenus = new Set()
    this._outsideSince = 0
    this._settle = 0
    this._watch = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 100, () => {
      this._checkPointer()
      return GLib.SOURCE_CONTINUE
    })
  }
  _pointerOverPanel() {
    const [x,y] = global.get_pointer()
    const [px,py] = this.panel.get_transformed_position()
    const [w,h] = this.panel.get_transformed_size()
    return x>=px && x<px+w && y>=py && y<py+h
  }
  _pointerOverExcludedArea() {
    const [x,y] = global.get_pointer()
    // Panel controls are often St.Widget rather than St.Button. Exclude
    // their whole allocated groups, including padding between indicators.
    const entries = Object.entries(this.taskbar.dtpPanel.allocationMap || {})
    return entries.some(([name,entry]) => {
      const actor = entry.actor
      if (name === 'taskbar' || !actor || !actor.mapped || !actor.visible) return false
      const [px,py] = actor.get_transformed_position()
      const [w,h] = actor.get_transformed_size()
      return w>0 && h>0 && x>=px && x<px+w && y>=py && y<py+h
    })
  }
  _checkPointer() {
    if (this._pointerOverPanel()) {
      this._outsideSince = 0
      if (!this._idleRevealed && !this._pointerOverExcludedArea()) {
        const [x,y] = global.get_pointer()
        const picked = global.stage.get_actor_at_pos(Clutter.PickMode.REACTIVE,x,y)
        // Empty panel surfaces reveal favorites; existing controls keep their actions.
        let actor = picked
        let interactive = false
        while (actor && actor !== this.panel) {
          if (actor instanceof St.Button || actor._delegate?.app) {
            interactive = true
            break
          }
          actor = actor.get_parent()
        }
        if (!interactive && actor === this.panel) this._setIdleRevealed(true)
      }
    } else if (!this._openItemMenus.size && !this.taskbar.previewMenu?.opened && !this.taskbar._dragMonitor) {
      const now = GLib.get_monotonic_time()
      this._outsideSince ||= now
      if (now-this._outsideSince>=400000) this._setIdleRevealed(false)
    } else this._outsideSince=0
  }
  _setIdleRevealed(value) {
    if (this._idleRevealed===value) return
    this._idleRevealed=value
    this.taskbar._queueRedisplay()
  }
  filterInfos(infos) {
    return this._idleRevealed ? infos : infos.filter(info=>info.windows.length && !info.isLauncher)
  }
  afterRedisplay() {
    if (this._settle) GLib.source_remove(this._settle)
    this._settle=GLib.timeout_add(GLib.PRIORITY_DEFAULT,700,()=>{
      this._settle=0
      for (const item of this.taskbar._getTaskbarIcons()) {
        item.childScale=1
        item.childOpacity=255
        const child=item.child
        if (!child) continue
        child.remove_all_transitions()
        child.set_scale(1,1)
        child.opacity=255
        child.translation_y=0
        const texture=child._delegate?.icon?.icon
        if (texture) {
          texture.remove_all_transitions()
          texture.set_size(this.taskbar.iconSize,this.taskbar.iconSize)
        }
        item.queue_relayout()
      }
      this.taskbar._box.queue_relayout()
      return GLib.SOURCE_REMOVE
    })
  }
  animateItem(item,position) {
    if (!this._idleRevealed || !item.child) return
    const child=item.child
    child.opacity=0
    child.translation_y=8
    child.ease({opacity:255,translation_y:0,duration:180,delay:Math.min(position,10)*28,mode:Clutter.AnimationMode.EASE_OUT_QUAD})
  }
  itemMenuStateChanged(item,open) {
    if(open)this._openItemMenus.add(item)
    else this._openItemMenus.delete(item)
  }
  destroy() {
    if(this._watch)GLib.source_remove(this._watch)
    if(this._settle)GLib.source_remove(this._settle)
    this._watch=this._settle=0
    this._openItemMenus.clear()
  }
}
