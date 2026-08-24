LICENSE
=======

Table of contents
-----------------
A. The overall license setup for MakeHuman
B. The license for the source code as such
C. The license for the bundled assets
D. Concerning the output from MakeHuman
E. human-api (network facade)


A. The overall license setup for MakeHuman
------------------------------------------

The MakeHuman application consists of two separate parts:

* Source code: the program logic that powers the application. 
* Assets: The graphical data that the application operates on

This repository is a MakeHuman tree plus a headless HTTP facade (`service/`,
aka **human-api**). Sections A–D are the upstream MakeHuman license statement.
Section E records how that statement applies when the same code is offered as
a network service.

B. The license for the source code as such
------------------------------------------

The MakeHuman source code is defined as files that contain program logic.
This includes python files, bat scripts, shell scripts and glsl shaders.

Image files required for the user interface as such are also covered. This
includes images for buttons, icons, and slider images.

The MakeHuman source (as defined per the above) is released under AGPL.

Copyright (C) 2001-2020  MakeHuman Team (www.makehumancommunity.org)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
   
For the full text of the source code license, see 
[LICENSE.CODE.md](LICENSE.CODE.md)

C. The license for the bundled assets
-------------------------------------

The assets are defined as any data contributing to the graphical output of
MakeHuman. This includes:

* The base mesh and proxies
* Targets and modifiers
* Textures
* Clothes (any MHCLO-based asset)
* Poses and expressions

These assets have been released under CC0 1.0 Universal. In summary this means
that to the fullest extent possible, it is the intention of the MakeHuman 
project that anyone can do whatever they want with it.

For the full text of the legal statement regarding the assets, see
[LICENSE.ASSETS.md](LICENSE.ASSETS.md)

D. Concerning the output from MakeHuman
---------------------------------------

It is the opinion of the MakeHuman project that no output from MakeHuman
contains any trace of program logic. That is, regardless of whether you use
the UI as such or if you call functions of MakeHuman via a script (such as 
via the blender importer), what you get is a combination of assets and your
own creative input. As the assets have been released under CC0, there is no
limitation on what you can do with this combined output.

To make it clear, the MakeHuman project makes no claim whatsoever over output
such as:

* Exports to files (FBX, OBJ, DAE, MHX2...)
* Exports via direct integration (import via MPFB)
* Graphical data generated via scripting or plugins
* Renderings
* Screenshots
* Saved model files

We regard these things as your data, which is yours to handle as you see
fit.

Note that what is discussed here are only assets bundled in the MakeHuman 
distribution. If you use a third part asset, such as one downloaded from the 
asset repositories, it is your own responsibility to make sure you abide by
its specific license. That license might be different from the one covering
the assets bundled by MakeHuman.

E. human-api (network facade)
-----------------------------

### Source code of this repository

All program logic in this repository — including upstream MakeHuman under
`makehuman/` and the headless HTTP modules under `service/` — remains under
the **GNU Affero General Public License v3** (or later), as in section B and
[LICENSE.CODE.md](LICENSE.CODE.md).

Copyright for MakeHuman source remains with the MakeHuman Team as stated above.
Additional facade and integration code under `service/` is part of the same
AGPL covered work.

### Bundled assets and exports

Sections C and D still apply unchanged:

* Bundled assets → **CC0 1.0** ([LICENSE.ASSETS.md](LICENSE.ASSETS.md))
* Exported meshes (OBJ and similar) from human-api → **user data** per section D
  (combination of CC0 assets and the caller’s parameters / creative input)

### Network use (AGPL §13)

When human-api is reachable over a network, operators must offer Corresponding
Source of the running covered work to users of that service. In this tree:

* `GET /license` returns a machine-readable pointer (AGPL-3.0, source URL,
  note that exported OBJ is user data)
* Full texts live in this repository: `LICENSE.md`, `LICENSE.CODE.md`,
  `LICENSE.ASSETS.md`

Default source URL advertised by the service:

`https://github.com/bobbythecode/3d-next-human`

### Separate callers (not AGPL merely by calling human-api)

Calling human-api over HTTP from a separate program does **not** by itself
make that program AGPL. Copying, importing, or bundling this repository’s
Python into another product does.

This section is an engineering boundary for operators of human-api, not legal advice.
