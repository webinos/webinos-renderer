# Copyright (c) 2011 The Chromium Embedded Framework Authors. All rights
# reserved. Use of this source code is governed by a BSD-style license that
# can be found in the LICENSE file.

{
  'variables': {
    'pkg-config': 'pkg-config',
    'chromium_code': 1,
    'grit_out_dir': '<(SHARED_INTERMEDIATE_DIR)/cef',
    'about_credits_file': '<(SHARED_INTERMEDIATE_DIR)/about_credits.html',
    'revision': '<!(python tools/revision.py)',
    # Need to be creative to match dylib version formatting requirements.
    'version_mac_dylib':
        '<!(python ../chrome/tools/build/version.py -f VERSION -f ../chrome/VERSION -t "@CEF_MAJOR@<(revision).@BUILD_HI@.@BUILD_LO@" -e "BUILD_HI=int(BUILD)/256" -e "BUILD_LO=int(BUILD)%256")',
  },
  'includes': [
    # Bring in the source file lists.
    'webinosBrowser_paths.gypi',
  ],
  'targets': [
   {
      'target_name': 'webinosBrowser',
      'type': 'executable',
      'mac_bundle': 1,
      'msvs_guid': '6617FED9-C5D4-4907-BF55-A90062A6683F',
      'dependencies': [
        'cef_pak',
        'libcef',
        'libcef_dll_wrapper',
#        '<(DEPTH)/build/temp_gyp/googleurl.gyp:googleurl',
        '<(DEPTH)/net/net.gyp:net',
      ],
      'defines': [
        'USING_CEF_SHARED',
      ],
      'include_dirs': [
        '.',
        # webinosBrowser includes are relative to the tests directory to make
        # creation of binary releases easier.
        # 'tests'
      ],
      'sources': [
        '<@(includes_common)',
        '<@(includes_wrapper)',
        '<@(webinosBrowser_sources_common)',
      ],
      'mac_bundle_resources': [
        '<@(webinosBrowser_bundle_resources_mac)',
      ],
      'mac_bundle_resources!': [
        # TODO(mark): Come up with a fancier way to do this (mac_info_plist?)
        # that automatically sets the correct INFOPLIST_FILE setting and adds
        # the file to a source group.
        'webinosBrowser/mac/Info.plist',
      ],
      'xcode_settings': {
        'INFOPLIST_FILE': 'webinosBrowser/mac/Info.plist',
        # Necessary to avoid an "install_name_tool: changing install names or
        # rpaths can't be redone" error.
        'OTHER_LDFLAGS': ['-Wl,-headerpad_max_install_names'],
      },
      'conditions': [
        ['OS=="win" and win_use_allocator_shim==1', {
          'dependencies': [
            '<(DEPTH)/base/allocator/allocator.gyp:allocator',
          ],
        }],
        ['OS=="win"', {
          'configurations': {
            'Debug_Base': {
              'msvs_settings': {
                'VCLinkerTool': {
                  'LinkIncremental': '<(msvs_large_module_debug_link_mode)',
                },
              },
            },
          },
          'msvs_settings': {
            'VCLinkerTool': {
              # Set /SUBSYSTEM:WINDOWS.
              'SubSystem': '2',
              'EntryPointSymbol' : 'wWinMainCRTStartup',
            },
          },
          'link_settings': {
            'libraries': [
              '-lcomctl32.lib',
              '-lshlwapi.lib',
              '-lrpcrt4.lib',
              '-lopengl32.lib',
              '-lglu32.lib',
            ],
          },
          'sources': [
            '<@(includes_win)',
            '<@(webinosBrowser_sources_win)',
          ],
        }],
        ['OS == "win" or (toolkit_uses_gtk == 1 and selinux == 0)', {
          'dependencies': [
            '<(DEPTH)/sandbox/sandbox.gyp:sandbox',
          ],
        }],
        [ 'OS=="mac"', {
          'product_name': 'webinosBrowser',
          'dependencies': [
            'webinosBrowser_helper_app',
            'interpose_dependency_shim',
          ],
          'variables': {
            'PRODUCT_NAME': 'webinosBrowser',
          },
          'copies': [
            {
              # Add library dependencies to the bundle.
              'destination': '<(PRODUCT_DIR)/<(PRODUCT_NAME).app/Contents/Frameworks/Chromium Embedded Framework.framework/Libraries/',
              'files': [
                '<(PRODUCT_DIR)/libcef.dylib',
                '<(PRODUCT_DIR)/ffmpegsumo.so',
              ],
            },
            {
              # Add the helper app.
              'destination': '<(PRODUCT_DIR)/<(PRODUCT_NAME).app/Contents/Frameworks',
              'files': [
                '<(PRODUCT_DIR)/<(PRODUCT_NAME) Helper.app',
                '<(PRODUCT_DIR)/libplugin_carbon_interpose.dylib',
              ],
            },
          ],
          'postbuilds': [
            {
              'postbuild_name': 'Fix Framework Link',
              'action': [
                'install_name_tool',
                '-change',
                '@executable_path/libcef.dylib',
                '@executable_path/../Frameworks/Chromium Embedded Framework.framework/Libraries/libcef.dylib',
                '${BUILT_PRODUCTS_DIR}/${EXECUTABLE_PATH}'
              ],
            },
            {
              'postbuild_name': 'Copy WebCore Resources',
              'action': [
                'cp',
                '-Rf',
                '${BUILT_PRODUCTS_DIR}/../../third_party/WebKit/Source/WebCore/Resources/',
                '${BUILT_PRODUCTS_DIR}/${PRODUCT_NAME}.app/Contents/Frameworks/Chromium Embedded Framework.framework/Resources/'
              ],
            },
            {
              'postbuild_name': 'Copy locale Resources',
              'action': [
                'cp',
                '-Rf',
                '${BUILT_PRODUCTS_DIR}/locales/',
                '${BUILT_PRODUCTS_DIR}/${PRODUCT_NAME}.app/Contents/Frameworks/Chromium Embedded Framework.framework/Resources/'
              ],
            },
            {
              'postbuild_name': 'Copy cef.pak File',
              'action': [
                'cp',
                '-f',
                '${BUILT_PRODUCTS_DIR}/cef.pak',
                '${BUILT_PRODUCTS_DIR}/${PRODUCT_NAME}.app/Contents/Frameworks/Chromium Embedded Framework.framework/Resources/cef.pak'
              ],
            },
            {
              'postbuild_name': 'Copy devtools_resources.pak File',
              'action': [
                'cp',
                '-f',
                '${BUILT_PRODUCTS_DIR}/devtools_resources.pak',
                '${BUILT_PRODUCTS_DIR}/${PRODUCT_NAME}.app/Contents/Frameworks/Chromium Embedded Framework.framework/Resources/devtools_resources.pak'
              ],
            },
            {
              # Modify the Info.plist as needed.
              'postbuild_name': 'Tweak Info.plist',
              'action': ['../build/mac/tweak_info_plist.py',
                         '--scm=1'],
            },
            {
              # This postbuid step is responsible for creating the following
              # helpers:
              #
              # cefclient Helper EH.app and cefclient Helper NP.app are created
              # from cefclient Helper.app.
              #
              # The EH helper is marked for an executable heap. The NP helper
              # is marked for no PIE (ASLR).
              'postbuild_name': 'Make More Helpers',
              'action': [
                '../build/mac/make_more_helpers.sh',
                'Frameworks',
                'webinosBrowser',
              ],
            },
          ],
          'link_settings': {
            'libraries': [
              '$(SDKROOT)/System/Library/Frameworks/AppKit.framework',
              '$(SDKROOT)/System/Library/Frameworks/OpenGL.framework',
            ],
          },
          'sources': [
            '<@(includes_mac)',
            '<@(webinosBrowser_sources_mac)',
          ],
        }],
        [ 'OS=="linux" or OS=="freebsd" or OS=="openbsd"', {
          'dependencies': [
            '<(DEPTH)/build/linux/system.gyp:gtk',
          ],
          'sources': [
            '<@(includes_linux)',
            '<@(webinosBrowser_sources_linux)',
          ],
          'copies': [
            {
              'destination': '<(PRODUCT_DIR)/files',
              'files': [
                '<@(webinosBrowser_bundle_resources_linux)',
              ],
            },
          ],
        }],
      ],
    },
  ],
}
