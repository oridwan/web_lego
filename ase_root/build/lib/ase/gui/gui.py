# fmt: off

import pickle
import subprocess
import sys
from functools import partial
from time import time

import numpy as np

import ase.gui.ui as ui
from ase import Atoms, __version__
from ase.gui.defaults import read_defaults
from ase.gui.i18n import _
from ase.gui.images import Images
from ase.gui.nanoparticle import SetupNanoparticle
from ase.gui.nanotube import SetupNanotube
from ase.gui.observer import Observers
from ase.gui.save import save_dialog
from ase.gui.settings import Settings
from ase.gui.status import Status
from ase.gui.surfaceslab import SetupSurfaceSlab
from ase.gui.view import View


class GUIObservers:
    def __init__(self):
        self.new_atoms = Observers()
        self.set_atoms = Observers()
        self.draw = Observers()


class GUI(View):
    ARROWKEY_SCAN = 0
    ARROWKEY_MOVE = 1
    ARROWKEY_ROTATE = 2

    def __init__(self, images=None,
                 rotations='',
                 show_bonds=False, expr=None):

        if not isinstance(images, Images):
            images = Images(images)

        self.images = images

        # Ordinary observers seem unused now, delete?
        self.observers = []
        self.obs = GUIObservers()

        self.config = read_defaults()
        if show_bonds:
            self.config['show_bonds'] = True

        menu = self.get_menu_data()

        self.window = ui.ASEGUIWindow(close=self.exit, menu=menu,
                                      config=self.config, scroll=self.scroll,
                                      scroll_event=self.scroll_event,
                                      press=self.press, move=self.move,
                                      release=self.release,
                                      resize=self.resize)

        super().__init__(rotations)
        self.status = Status(self)

        self.subprocesses = []  # list of external processes
        self.movie_window = None
        self.simulation = {}  # Used by modules on Calculate menu.
        self.module_state = {}  # Used by modules to store their state.

        self.arrowkey_mode = self.ARROWKEY_SCAN
        self.move_atoms_mask = None

        self.set_frame(len(self.images) - 1, focus=True)

        # Used to move the structure with the mouse
        self.prev_pos = None
        self.last_scroll_time = time()
        self.orig_scale = self.scale

        if len(self.images) > 1:
            self.movie()

        if expr is None:
            expr = self.config['gui_graphs_string']

        if expr is not None and expr != '' and len(self.images) > 1:
            self.plot_graphs(expr=expr, ignore_if_nan=True)

    @property
    def moving(self):
        return self.arrowkey_mode != self.ARROWKEY_SCAN

    def run(self):
        self.window.run()

    def toggle_move_mode(self, key=None):
        self.toggle_arrowkey_mode(self.ARROWKEY_MOVE)

    def toggle_rotate_mode(self, key=None):
        self.toggle_arrowkey_mode(self.ARROWKEY_ROTATE)

    def toggle_arrowkey_mode(self, mode):
        # If not currently in given mode, activate it.
        # Else, deactivate it (go back to SCAN mode)
        assert mode != self.ARROWKEY_SCAN

        if self.arrowkey_mode == mode:
            self.arrowkey_mode = self.ARROWKEY_SCAN
            self.move_atoms_mask = None
        else:
            self.arrowkey_mode = mode
            self.move_atoms_mask = self.images.selected.copy()

        self.draw()

    def step(self, key):
        d = {'Home': -10000000,
             'Page-Up': -1,
             'Page-Down': 1,
             'End': 10000000}[key]
        i = max(0, min(len(self.images) - 1, self.frame + d))
        self.set_frame(i)
        if self.movie_window is not None:
            self.movie_window.frame_number.value = i

    def copy_image(self, key=None):
        self.images._images.append(self.atoms.copy())
        self.images.filenames.append(None)

        if self.movie_window is not None:
            self.movie_window.frame_number.scale.configure(to=len(self.images))
        self.step('End')

    def _do_zoom(self, x):
        """Utility method for zooming"""
        self.scale *= x
        self.draw()

    def zoom(self, key):
        """Zoom in/out on keypress or clicking menu item"""
        x = {'+': 1.2, '-': 1 / 1.2}[key]
        self._do_zoom(x)

    def scroll_event(self, event):
        """Zoom in/out when using mouse wheel"""
        SHIFT = event.modifier == 'shift'
        x = 1.0
        if event.button == 4 or event.delta > 0:
            x = 1.0 + (1 - SHIFT) * 0.2 + SHIFT * 0.01
        elif event.button == 5 or event.delta < 0:
            x = 1.0 / (1.0 + (1 - SHIFT) * 0.2 + SHIFT * 0.01)
        self._do_zoom(x)

    def settings(self):
        return Settings(self)

    def scroll(self, event):
        shift = 0x1
        ctrl = 0x4
        alt_l = 0x8
        mac_option_key = 0x10

        use_small_step = bool(event.state & shift)
        rotate_into_plane = bool(event.state & (ctrl | alt_l | mac_option_key))

        dxdydz = {'up': (0, 1 - rotate_into_plane, rotate_into_plane),
                  'down': (0, -1 + rotate_into_plane, -rotate_into_plane),
                  'right': (1, 0, 0),
                  'left': (-1, 0, 0)}.get(event.key, None)

        # Get scroll direction using shift + right mouse button
        # event.type == '6' is mouse motion, see:
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-types.html
        if event.type == '6':
            cur_pos = np.array([event.x, -event.y])
            # Continue scroll if button has not been released
            if self.prev_pos is None or time() - self.last_scroll_time > .5:
                self.prev_pos = cur_pos
                self.last_scroll_time = time()
            else:
                dxdy = cur_pos - self.prev_pos
                dxdydz = np.append(dxdy, [0])
                self.prev_pos = cur_pos
                self.last_scroll_time = time()

        if dxdydz is None:
            return

        vec = 0.1 * np.dot(self.axes, dxdydz)
        if use_small_step:
            vec *= 0.1

        if self.arrowkey_mode == self.ARROWKEY_MOVE:
            self.atoms.positions[self.move_atoms_mask[:len(self.atoms)]] += vec
            self.set_frame()
        elif self.arrowkey_mode == self.ARROWKEY_ROTATE:
            # For now we use atoms.rotate having the simplest interface.
            # (Better to use something more minimalistic, obviously.)
            mask = self.move_atoms_mask[:len(self.atoms)]
            center = self.atoms.positions[mask].mean(axis=0)
            tmp_atoms = self.atoms[mask]
            tmp_atoms.positions -= center
            tmp_atoms.rotate(50 * np.linalg.norm(vec), vec)
            self.atoms.positions[mask] = tmp_atoms.positions + center
            self.set_frame()
        else:
            # The displacement vector is scaled
            # so that the cursor follows the structure
            # Scale by a third works for some reason
            scale = self.orig_scale / (3 * self.scale)
            self.center -= vec * scale

            # dx * 0.1 * self.axes[:, 0] - dy * 0.1 * self.axes[:, 1])

            self.draw()

    def delete_selected_atoms(self, widget=None, data=None):
        import ase.gui.ui as ui
        nselected = sum(self.images.selected)
        if nselected and ui.ask_question(_('Delete atoms'),
                                         _('Delete selected atoms?')):
            self.really_delete_selected_atoms()

    def really_delete_selected_atoms(self):
        mask = self.images.selected[:len(self.atoms)]
        del self.atoms[mask]

        # Will remove selection in other images, too
        self.images.selected[:] = False
        self.set_frame()
        self.draw()

    def constraints_window(self):
        from ase.gui.constraints import Constraints
        return Constraints(self)

    def select_all(self, key=None):
        self.images.selected[:] = True
        self.draw()

    def invert_selection(self, key=None):
        self.images.selected[:] = ~self.images.selected
        self.draw()

    def select_constrained_atoms(self, key=None):
        self.images.selected[:] = ~self.images.get_dynamic(self.atoms)
        self.draw()

    def select_immobile_atoms(self, key=None):
        if len(self.images) > 1:
            R0 = self.images[0].positions
            for atoms in self.images[1:]:
                R = atoms.positions
                self.images.selected[:] = ~(np.abs(R - R0) > 1.0e-10).any(1)
        self.draw()

    def movie(self):
        from ase.gui.movie import Movie
        self.movie_window = Movie(self)

    def plot_graphs(self, key=None, expr=None, ignore_if_nan=False):
        from ase.gui.graphs import Graphs
        g = Graphs(self)
        if expr is not None:
            g.plot(expr=expr, ignore_if_nan=ignore_if_nan)

    def pipe(self, task, data):
        process = subprocess.Popen([sys.executable, '-m', 'ase.gui.pipe'],
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        pickle.dump((task, data), process.stdin)
        process.stdin.close()
        # Either process writes a line, or it crashes and line becomes ''
        line = process.stdout.readline().decode('utf8').strip()

        if line != 'GUI:OK':
            if line == '':  # Subprocess probably crashed
                line = _('Failure in subprocess')
            self.bad_plot(line)
        else:
            self.subprocesses.append(process)
        return process

    def bad_plot(self, err, msg=''):
        ui.error(_('Plotting failed'), '\n'.join([str(err), msg]).strip())

    def neb(self):
        from ase.utils.forcecurve import fit_images
        try:
            forcefit = fit_images(self.images)
        except Exception as err:
            self.bad_plot(err, _('Images must have energies and forces, '
                                 'and atoms must not be stationary.'))
        else:
            self.pipe('neb', forcefit)

    def bulk_modulus(self):
        try:
            v = [abs(np.linalg.det(atoms.cell)) for atoms in self.images]
            e = [self.images.get_energy(a) for a in self.images]
            from ase.eos import EquationOfState
            eos = EquationOfState(v, e)
            plotdata = eos.getplotdata()
        except Exception as err:
            self.bad_plot(err, _('Images must have energies '
                                 'and varying cell.'))
        else:
            self.pipe('eos', plotdata)

    def reciprocal(self):
        if self.atoms.cell.rank != 3:
            self.bad_plot(_('Requires 3D cell.'))
            return None

        cell = self.atoms.cell.uncomplete(self.atoms.pbc)
        bandpath = cell.bandpath(npoints=0)
        return self.pipe('reciprocal', bandpath)

    def open(self, button=None, filename=None):
        chooser = ui.ASEFileChooser(self.window.win)

        filename = filename or chooser.go()
        format = chooser.format
        if filename:
            try:
                self.images.read([filename], slice(None), format)
            except Exception as err:
                ui.show_io_error(filename, err)
                return  # Hmm.  Is self.images in a consistent state?
            self.set_frame(len(self.images) - 1, focus=True)

    def modify_atoms(self, key=None):
        from ase.gui.modify import ModifyAtoms
        return ModifyAtoms(self)

    def add_atoms(self, key=None):
        from ase.gui.add import AddAtoms
        return AddAtoms(self)

    def cell_editor(self, key=None):
        from ase.gui.celleditor import CellEditor
        return CellEditor(self)

    def quick_info_window(self, key=None):
        from ase.gui.quickinfo import info
        info_win = ui.Window(_('Quick Info'), wmtype='utility')
        info_win.add(info(self))

        # Update quickinfo window when we change frame
        def update(window):
            exists = window.exists
            if exists:
                # Only update if we exist
                window.things[0].text = info(self)
            return exists
        self.attach(update, info_win)
        return info_win

    def surface_window(self):
        return SetupSurfaceSlab(self)

    def nanoparticle_window(self):
        return SetupNanoparticle(self)

    def nanotube_window(self):
        return SetupNanotube(self)

    def new_atoms(self, atoms):
        "Set a new atoms object."
        rpt = getattr(self.images, 'repeat', None)
        self.images.repeat_images(np.ones(3, int))
        self.images.initialize([atoms])
        self.frame = 0  # Prevent crashes
        self.images.repeat_images(rpt)
        self.set_frame(frame=0, focus=True)
        self.obs.new_atoms.notify()

    def exit(self, event=None):
        for process in self.subprocesses:
            process.terminate()
        self.window.close()

    def new(self, key=None):
        subprocess.Popen([sys.executable, '-m', 'ase', 'gui'])

    def save(self, key=None):
        return save_dialog(self)

    def external_viewer(self, name):
        from ase.visualize import view
        return view(list(self.images), viewer=name)

    def selected_atoms(self):
        selection_mask = self.images.selected[:len(self.atoms)]
        return self.atoms[selection_mask]

    def wrap_atoms(self, key=None):
        """Wrap atoms around the unit cell."""
        for atoms in self.images:
            atoms.wrap()
        self.set_frame()

    @property
    def clipboard(self):
        from ase.gui.clipboard import AtomsClipboard
        return AtomsClipboard(self.window.win)

    def cut_atoms_to_clipboard(self, event=None):
        self.copy_atoms_to_clipboard(event)
        self.really_delete_selected_atoms()

    def copy_atoms_to_clipboard(self, event=None):
        atoms = self.selected_atoms()
        self.clipboard.set_atoms(atoms)

    def paste_atoms_from_clipboard(self, event=None):
        try:
            atoms = self.clipboard.get_atoms()
        except Exception as err:
            ui.error(
                'Cannot paste atoms',
                'Pasting currently works only with the ASE JSON format.\n\n'
                f'Original error:\n\n{err}')
            return

        if self.atoms == Atoms():
            self.atoms.cell = atoms.cell
            self.atoms.pbc = atoms.pbc
        self.paste_atoms_onto_existing(atoms)

    def paste_atoms_onto_existing(self, atoms):
        selection = self.selected_atoms()
        if len(selection):
            paste_center = selection.positions.sum(axis=0) / len(selection)
            # atoms.center() is a no-op in directions without a cell vector.
            # But we actually want the thing centered nevertheless!
            # Therefore we have to set the cell.
            atoms = atoms.copy()
            atoms.cell = (1, 1, 1)  # arrrgh.
            atoms.center(about=paste_center)

        self.add_atoms_and_select(atoms)
        self.move_atoms_mask = self.images.selected.copy()
        self.arrowkey_mode = self.ARROWKEY_MOVE
        self.draw()

    def add_atoms_and_select(self, new_atoms):
        atoms = self.atoms
        atoms += new_atoms

        if len(atoms) > self.images.maxnatoms:
            self.images.initialize(list(self.images),
                                   self.images.filenames)

        selected = self.images.selected
        selected[:] = False
        # 'selected' array may be longer than current atoms
        selected[len(atoms) - len(new_atoms):len(atoms)] = True

        self.set_frame()
        self.draw()

    def get_menu_data(self):
        M = ui.MenuItem
        return [
            (_('_File'),
             [M(_('_Open'), self.open, 'Ctrl+O'),
              M(_('_New'), self.new, 'Ctrl+N'),
              M(_('_Save'), self.save, 'Ctrl+S'),
              M('---'),
              M(_('_Quit'), self.exit, 'Ctrl+Q')]),

            (_('_Edit'),
             [M(_('Select _all'), self.select_all),
              M(_('_Invert selection'), self.invert_selection),
              M(_('Select _constrained atoms'), self.select_constrained_atoms),
              M(_('Select _immobile atoms'), self.select_immobile_atoms),
              # M('---'),
              M(_('_Cut'), self.cut_atoms_to_clipboard, 'Ctrl+X'),
              M(_('_Copy'), self.copy_atoms_to_clipboard, 'Ctrl+C'),
              M(_('_Paste'), self.paste_atoms_from_clipboard, 'Ctrl+V'),
              M('---'),
              M(_('Hide selected atoms'), self.hide_selected),
              M(_('Show selected atoms'), self.show_selected),
              M('---'),
              M(_('_Modify'), self.modify_atoms, 'Ctrl+Y'),
              M(_('_Add atoms'), self.add_atoms, 'Ctrl+A'),
              M(_('_Delete selected atoms'), self.delete_selected_atoms,
                'Backspace'),
              M(_('Edit _cell'), self.cell_editor, 'Ctrl+E'),
              M('---'),
              M(_('_First image'), self.step, 'Home'),
              M(_('_Previous image'), self.step, 'Page-Up'),
              M(_('_Next image'), self.step, 'Page-Down'),
              M(_('_Last image'), self.step, 'End'),
              M(_('Append image copy'), self.copy_image)]),

            (_('_View'),
             [M(_('Show _unit cell'), self.toggle_show_unit_cell, 'Ctrl+U',
                value=self.config['show_unit_cell']),
              M(_('Show _axes'), self.toggle_show_axes,
                value=self.config['show_axes']),
              M(_('Show _bonds'), self.toggle_show_bonds, 'Ctrl+B',
                value=self.config['show_bonds']),
              M(_('Show _velocities'), self.toggle_show_velocities, 'Ctrl+G',
                value=False),
              M(_('Show _forces'), self.toggle_show_forces, 'Ctrl+F',
                value=False),
              M(_('Show _magmoms'), self.toggle_show_magmoms,
                value=False),
              M(_('Show _Labels'), self.show_labels,
                choices=[_('_None'),
                         _('Atom _Index'),
                         _('_Magnetic Moments'),  # XXX check if exist
                         _('_Element Symbol'),
                         _('_Initial Charges'),  # XXX check if exist
                         ]),
              M('---'),
              M(_('Quick Info ...'), self.quick_info_window, 'Ctrl+I'),
              M(_('Repeat ...'), self.repeat_window, 'R'),
              M(_('Rotate ...'), self.rotate_window),
              M(_('Colors ...'), self.colors_window, 'C'),
              # TRANSLATORS: verb
              M(_('Focus'), self.focus, 'F'),
              M(_('Zoom in'), self.zoom, '+'),
              M(_('Zoom out'), self.zoom, '-'),
              M(_('Change View'),
                submenu=[
                    M(_('Reset View'), self.reset_view, '='),
                    M(_('xy-plane'), self.set_view, 'Z'),
                    M(_('yz-plane'), self.set_view, 'X'),
                    M(_('zx-plane'), self.set_view, 'Y'),
                    M(_('yx-plane'), self.set_view, 'Alt+Z'),
                    M(_('zy-plane'), self.set_view, 'Alt+X'),
                    M(_('xz-plane'), self.set_view, 'Alt+Y'),
                    M(_('a2,a3-plane'), self.set_view, '1'),
                    M(_('a3,a1-plane'), self.set_view, '2'),
                    M(_('a1,a2-plane'), self.set_view, '3'),
                    M(_('a3,a2-plane'), self.set_view, 'Alt+1'),
                    M(_('a1,a3-plane'), self.set_view, 'Alt+2'),
                    M(_('a2,a1-plane'), self.set_view, 'Alt+3')]),
              M(_('Settings ...'), self.settings),
              M('---'),
              M(_('VMD'), partial(self.external_viewer, 'vmd')),
              M(_('RasMol'), partial(self.external_viewer, 'rasmol')),
              M(_('xmakemol'), partial(self.external_viewer, 'xmakemol')),
              M(_('avogadro'), partial(self.external_viewer, 'avogadro'))]),

            (_('_Tools'),
             [M(_('Graphs ...'), self.plot_graphs),
              M(_('Movie ...'), self.movie),
              M(_('Constraints ...'), self.constraints_window),
              M(_('Render scene ...'), self.render_window),
              M(_('_Move selected atoms'), self.toggle_move_mode, 'Ctrl+M'),
              M(_('_Rotate selected atoms'), self.toggle_rotate_mode,
                'Ctrl+R'),
              M(_('NE_B plot'), self.neb),
              M(_('B_ulk Modulus'), self.bulk_modulus),
              M(_('Reciprocal space ...'), self.reciprocal),
              M(_('Wrap atoms'), self.wrap_atoms, 'Ctrl+W')]),

            # TRANSLATORS: Set up (i.e. build) surfaces, nanoparticles, ...
            (_('_Setup'),
             [M(_('_Surface slab'), self.surface_window, disabled=False),
              M(_('_Nanoparticle'),
                self.nanoparticle_window),
              M(_('Nano_tube'), self.nanotube_window)]),

            # (_('_Calculate'),
            # [M(_('Set _Calculator'), self.calculator_window, disabled=True),
            #  M(_('_Energy and Forces'), self.energy_window, disabled=True),
            #  M(_('Energy Minimization'), self.energy_minimize_window,
            #    disabled=True)]),

            (_('_Help'),
             [M(_('_About'), partial(ui.about, 'ASE-GUI',
                                     version=__version__,
                                     webpage='https://wiki.fysik.dtu.dk/'
                                     'ase/ase/gui/gui.html')),
              M(_('Webpage ...'), webpage)])]

    def attach(self, function, *args, **kwargs):
        self.observers.append((function, args, kwargs))

    def call_observers(self):
        # Use function return value to determine if we keep observer
        self.observers = [(function, args, kwargs) for (function, args, kwargs)
                          in self.observers if function(*args, **kwargs)]

    def repeat_poll(self, callback, ms, ensure_update=True):
        """Invoke callback(gui=self) every ms milliseconds.

        This is useful for polling a resource for updates to load them
        into the GUI.  The GUI display will be hence be updated after
        each call; pass ensure_update=False to circumvent this.

        Polling stops if the callback function raises StopIteration.

        Example to run a movie manually, then quit::

            from ase.collections import g2
            from ase.gui.gui import GUI

            names = iter(g2.names)

            def main(gui):
                try:
                    name = next(names)
                except StopIteration:
                    gui.window.win.quit()
                else:
                    atoms = g2[name]
                    gui.images.initialize([atoms])

            gui = GUI()
            gui.repeat_poll(main, 30)
            gui.run()"""

        def callbackwrapper():
            try:
                callback(gui=self)
            except StopIteration:
                pass
            finally:
                # Reinsert self so we get called again:
                self.window.win.after(ms, callbackwrapper)

            if ensure_update:
                self.set_frame()
                self.draw()

        self.window.win.after(ms, callbackwrapper)


def webpage():
    import webbrowser
    webbrowser.open('https://wiki.fysik.dtu.dk/ase/ase/gui/gui.html')
