# Home menu

The standard Dark/Light home launcher defaults to one row. Emulators and the
Ports shelf precede apps; Favorites and Recently played follow them. A saved
custom order takes precedence over that default grouping. The upper panel keeps
the selected item's normal preview; the lower panel contains the icon grid.

- **A** opens the selected emulator/app. Tap an icon to select it, then tap it
  again to open it. D-pad moves selection; L/R or the top arrows change page.
- **X** enters editing. A picks up the selected icon; move the cursor with the
  D-pad, then A places it. Touch can pick up and place too. B cancels a picked-up
  move. X, or B without an icon picked up, finishes editing.
- **−** zooms out by adding a row; **+** zooms in by removing one. One to four
  rows are supported. In editing, L is − and R is +.
- **Y** in editing, or **Ports: shelf / Ports: home**, toggles installed ports on
  home. Finish/cancel a picked-up move before changing port visibility.
  PortMaster itself stays in the Ports shelf. These are OS shortcuts: the
  PortMaster installation, port launch scripts and app update streams are unchanged.
- START settings and SELECT search are available after finishing editing.

The OS atomically saves rows, port visibility and stable tile IDs in writable
`/data/banana/home-layout.conf`. No firmware rebuild is needed to retain a layout.
App installs/removals do not reuse another app's position; IDs for absent items
remain saved, and new entries follow the saved entries. Removing this one file
while the launcher is stopped restores the default layout, without touching
installed apps, games, saves or other settings.

Home shortcuts for ports share the original port's play statistics and favorites.
Search, Favorites and Recently played use canonical port entries, so showing a
port on home does not duplicate it in those collections. Collection mappings are
updated when icons move; they continue launching through the original system.

The Ports library, PortMaster UI and Slopetanium library layout are separate from
this first home-menu change.
