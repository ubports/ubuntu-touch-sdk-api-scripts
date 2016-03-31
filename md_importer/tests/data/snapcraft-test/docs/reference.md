
# Snapcraft reference

`snapcraft` comes with a handy help system, just run:
```
$ snapcraft help
```
to get you started.

Here we want to provide you with the current documentation from within
snappy. It's a reference of `snapcraft`'s plugins and internals.

## Internal documentation

### Topic: Sources

Common keywords for plugins that use common source options.

A part that uses common source options can have these keyword entries:

    - source:
      (string)
      A path to some source tree to build. It can be either remote or local,
      and either a directory tree or a tarball.
    - source-type:
      (string)
      In some cases the source is not enough to identify the version control
      system or compression algorithim. This hints the system into what to
      do, the valid values are:

                   - bzr
                   - mercurial
                   - hg
                   - git
                   - tar

    - source-branch:
      (string)
      A specific branch from the source tree. This will result in an error
      if used with a bazaar source type.
    - source-tag:
      (string)
      A specific tag from the source tree.
    - source-subdir:
      (string)
      A source directory within a repository or tarfile to enter and build
      from.


### Topic: Plugins

Plugins drive the build process for a part.
Each part can use an individual plugin that understands how to work with
the declared sources.

These plugins have a lifecycle that consists of the following steps:

    - pull
    - build
    - stage
    - strip
    - snap

#### Lifecycle

##### Pull
This is the first step. This is where content is downloaded, e.g. checkout a
git repository or download a binary component like the Java SDK. Snapcraft
will place the downloaded content for each part in that part's
`parts/<part-name>/src` directory.

##### Build
This is the step that follows pull. Each part is built in its
`parts/part-name/build` directory and installs itself into
`parts/part-name/install`.

##### Stage
After the build step of each part, the parts are combined into a single
directory tree that is called the "staging area". It can be found
under the `./stage` directory.

This is the area where all parts can share assets such as libraries to link
against.

##### Strip
The strip step moves the data into a `./snap` directory. It contains only
the content that will be put into the final snap package, unlike the staging
area which may include some development files not destined for your package.

The Snappy metadata information about your project will also now be placed
in `./snap/meta`.

This `./snap` directory is useful for inspecting what is going into your
snap and to make any final post-processing on snapcraft's output.

##### Snap
The final step builds a snap package out of the `snap` directory.

#### Common keywords

There are common builtin keywords provided to a snapcraft plugin which can
be used in any part irrespective of the plugin, these are

    - after:
      (list of strings)
      Specifies any parts that should be built before this part is.  This
      is mostly useful when a part needs a library or build tool built by
      another part.
      If a part listed in `after` is not defined locally, it will be
      searched for in the wiki (https://wiki.ubuntu.com/Snappy/Wiki)
    - stage-packages:
      (list of strings)
      A list of Ubuntu packages to use that are needed to support the part
      creation.
    - build-packages:
      (list of strings)
      A list of Ubuntu packages to be installed on the host to aid in
      building the part. These packages will not go into the final snap.
    - organize:
      (yaml subsection)
      A dictionary exposing replacements, the key is the internal filename
      whilst the value is the exposed filename, filesets will refer to the
      exposed named applied after organization is applied.
      This can be used to avoid conflicts by renaming files or using a
      different layout from what came out of the build, e.g.;
      `/usr/local/share/icon.png` -> `/usr/share/icon.png`.
    - filesets:
      (yaml subsection)
      A dictionary with filesets, the key being a recognizable user defined
      string and its value a list of filenames to be included or
      excluded. Globbing is achieved with * for either inclusions or
      exclusion. Exclusions are denoted by an initial `-`.
      Globbing is computed from the part's install directory in
      `parts/<part-name>/install`.
    - stage:
      (list of strings)
      A list of files from a part’s installation to expose in `stage`.
      Rules applying to the list here are the same as those of filesets.
      Referencing of fileset keys is done with a $ prefixing the fileset
      key, which will expand with the value of such key.
    - snap:
      (list of strings)
      A list of files from a part’s installation to expose in `snap`.
      Rules applying to the list here are the same as those of filesets.
      Referencing of fileset keys is done with a $ prefixing the fileset
      key, which will expand with the value of such key.



## snapcraft's Plugins

In this section we are going to discuss `snapcraft`'s plugins, their workflow
and their options.

### The ant plugin

The ant plugin is useful for ant based parts.

The ant build system is commonly used to build Java projects.
The plugin requires a build.xml in the root of the source tree.

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.


### The autotools plugin

The autotools plugin is used for autotools based parts.

Autotools based projects are the ones that have the usual
`./configure && make && make install` instruction set.

The plugin tries to build using ./configure first, if it is not there
it will run ./autogen and if autogen is not there it will run autoreconf.

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

In additon, this plugin uses the following plugin-specific keywords:

    - configflags:
      (list of strings)
      configure flags to pass to the build such as those shown by running
      './configure --help'


### The catkin plugin

The catkin plugin is useful for building ROS parts.

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

Additionally, this plugin uses the following plugin-specific keywords:

    - catkin-packages:
      (list of strings)
      List of catkin packages to build.
    - source-space:
      (string)
      The source space containing Catkin packages. By default this is 'src'.


### The cmake plugin

The cmake plugin is useful for building cmake based parts.

These are projects that have a CMakeLists.txt that drives the build.
The plugin requires a CMakeLists.txt in the root of the source tree.

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

Additionally, this plugin uses the following plugin-specific keywords:

    - configflags:
      (list of strings)
      configure flags to pass to the build using the common cmake semantics.


### The go plugin

The go plugin can be used for go projects using `go get`.

This plugin uses the common plugin keywords, for more information check the
'plugins' topic.

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

Additionally, this plugin uses the following plugin-specific keywords:

    - go-packages:
      (list of strings)
      Go packages to fetch, these must be a "main" package. Dependencies
      are pulled in automatically by `go get`.
      Packages that are not "main" will not cause an error, but would
      not be useful either.


### The make plugin

The make plugin is useful for building make based parts.

Make based projects are projects that have a Makefile that drives the
build.

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

Additionally, this plugin uses the following plugin-specific keyword:

    - makefile:
      (string)
      Use the given file as the makefile.


### The maven plugin

This plugin is useful for building parts that use maven.

The maven build system is commonly used to build Java projects.
The plugin requires a pom.xml in the root of the source tree.

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

Additionally, this plugin uses the following plugin-specific keywords:

    - maven-options:
      (list of strings)
      flags to pass to the build using the maven semantics for parameters.


### The nil plugin

The nil plugin is useful for parts with entirely built in properties.

The nil plugin allows parts that do nothing. As a result parts can be defined
that, for example, have no source, but can still make use of all the properties
available in snapcraft.


### The nodejs plugin

The nodejs plugin is useful for node/npm based parts.

The plugin uses node to install dependencies from `package.json`. It
also sets up binaries defined in `package.json` into the `PATH`.

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

Additionally, this plugin uses the following plugin-specific keywords:

    - node-packages:
      (list)
      A list of dependencies to fetch using npm.


### The python2 plugin

The python2 plugin can be used for python 2 based parts.

The python2 plugin can be used for python 2 projects where you would
want to do:

    - import python modules with a requirements.txt
    - build a python project that has a setup.py
    - install sources straight from pip

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

Additionally, this plugin uses the following plugin-specific keywords:

    - requirements:
      (string)
      path to a requirements.txt file
    - python-packages:
      (list)
      A list of dependencies to get from PyPi


### The python3 plugin

The python3 plugin can be used for python 3 based parts.

The python3 plugin can be used for python 3 projects where you would
want to do:

    - import python modules with a requirements.txt
    - build a python project that has a setup.py
    - install sources straight from pip

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

Additionally, this plugin uses the following plugin-specific keywords:

    - requirements:
      (string)
      path to a requirements.txt file
    - python-packages:
      (list)
      A list of dependencies to get from PyPi


### The scons plugin

The scons plugin is useful for building parts that build with scons.

These are projects that have a SConstruct that drives the build.

This plugin uses the common plugin keywords as well as those for "sources".
For more information check the 'plugins' topic for the former and the
'sources' topic for the latter.

Additionally, this plugin uses the following plugin-specific keywords:

    - scons-options:
      (list of strings)
      flags to pass to the build using the scons semantics for parameters.

