Changelog
=========

2.2.1
-----

- Merge branch 'hotfix/2.1.6' `a699822e5 <https://github.com/toscawidgets/tw2.core/commit/a699822e56031a1a0aa351f7bae19ff58401af18>`_
- compound_key was ignoring key for RepeatingWidget `ed0946146 <https://github.com/toscawidgets/tw2.core/commit/ed09461460775b9d8034ecfcb8cb8680a43c9fee>`_
- Fix for DisplayOnlyWidget in compound_id regression `11570e42e <https://github.com/toscawidgets/tw2.core/commit/11570e42e4dde2b03145bec36b949ad282cce845>`_
- All and Any validators didn't work with unicode error messages `3c177ad8d <https://github.com/toscawidgets/tw2.core/commit/3c177ad8d5a04d2913b8f62418b9a2b0e2dbfc7b>`_
- Merge branch 'master' of @amol-/tw2.core into develop `5254065c0 <https://github.com/toscawidgets/tw2.core/commit/5254065c01a362617956ce0adb08851884ee0596>`_

2.2.0.8
-------

- Fix duplicate class name `1c133c907 <https://github.com/toscawidgets/tw2.core/commit/1c133c9074aaded7823d99e3f31aaf4eab8f26d8>`_
- Be able to put an HTML separator between the children of a RepeatingWidget. We also need to support it for the CompoundWidget since it uses the same template `db717642d <https://github.com/toscawidgets/tw2.core/commit/db717642dff0b5b3cb69e7e3929a0ceaf08a2a54>`_
- Merge pull request #96 from LeResKP/develop `41229bf01 <https://github.com/toscawidgets/tw2.core/commit/41229bf01b079f49d4ba8747d2f530f4d0eddf99>`_
- Re-enable archive_tw2_resources on Python 2 `56215397a <https://github.com/toscawidgets/tw2.core/commit/56215397a2e5e373ca5dd44c28fedc4fc66c5d19>`_

2.2.0.7
-------

- * Clean up cache * Hack to fix the tests with empty value attributes for genshi `cd5febe2b <https://github.com/toscawidgets/tw2.core/commit/cd5febe2bc6c675fa8c7320731d4fe98c603c42d>`_
- Merge pull request #95 from LeResKP/develop `9f54d72be <https://github.com/toscawidgets/tw2.core/commit/9f54d72be754c6087a0a780c6d89e4761924af23>`_
- Merge branch 'develop' of github.com:toscawidgets/tw2.core into develop `9142fe165 <https://github.com/toscawidgets/tw2.core/commit/9142fe165139db87c761ca4ed17f673244e5a9b7>`_

2.2.0.6
-------


2.2.0.5
-------

- Add a setUp method back to another base test thats missing it. `55b6061ed <https://github.com/toscawidgets/tw2.core/commit/55b6061edf0264426910d1a19f5641ff0c3cf7a0>`_

2.2.0.4
-------

- Restore an old setUp method for tw2.core.testbase.WidgetTest `da2d9bab2 <https://github.com/toscawidgets/tw2.core/commit/da2d9bab2db86f2378525ad0930af3b1e48e3622>`_

2.2.0.3
-------

- Added a new validator `UUIDValidator` (+test) for UUID/GUIDs `ebea7f30b <https://github.com/toscawidgets/tw2.core/commit/ebea7f30b892eb426ca788b26112b5db6d845260>`_
- Merge pull request #92 from RobertSudwarts/amol `481926de6 <https://github.com/toscawidgets/tw2.core/commit/481926de62e14d37e1b102b7d8734a8cc576f9c2>`_
- Call me picky, but I think license belongs up there `de9d87587 <https://github.com/toscawidgets/tw2.core/commit/de9d8758795fb94662ff79b075cf125e6c7f6fb5>`_
- Merge branch 'amol' into develop `46d68b792 <https://github.com/toscawidgets/tw2.core/commit/46d68b792f2076e5862730abf464dbf3ec93362b>`_
- pep8 `5896d4db0 <https://github.com/toscawidgets/tw2.core/commit/5896d4db0d71d47641732423e7363a19cb8cd72f>`_
- Fix tests for UUIDValidator `bfc4531ec <https://github.com/toscawidgets/tw2.core/commit/bfc4531ecfb55a18a13827ad893469623f1b2aa1>`_
- Handle case where response.charset is None. `e1fe13460 <https://github.com/toscawidgets/tw2.core/commit/e1fe134605767385c3554d58066776596e8d9fba>`_
- Merge branch 'develop' of github.com:toscawidgets/tw2.core into develop `4fec80d22 <https://github.com/toscawidgets/tw2.core/commit/4fec80d221fe423c89485d3871073994bd3850ed>`_

2.2.0.2
-------

- Update one test now that the error message has changed. `c31f52732 <https://github.com/toscawidgets/tw2.core/commit/c31f52732ed6cd7cbe8dce6fd0671253721c5062>`_
- Catch if a template is None. `a159b6cf1 <https://github.com/toscawidgets/tw2.core/commit/a159b6cf1bf28f29063dcd00bd7db9af4d082985>`_
- Remove direct dependence on unittest so we can get test-generators working again.  Relates to #88. `f561ef33d <https://github.com/toscawidgets/tw2.core/commit/f561ef33d277401e661413e47d0a14249389fcb2>`_
- Turn the css/js escaping tests into generators per engine too. `c43bd4d7f <https://github.com/toscawidgets/tw2.core/commit/c43bd4d7f9b8855f2db417f4a5051a1bdb685b6f>`_
- Kajiki expects unicode these days. `16f6508c2 <https://github.com/toscawidgets/tw2.core/commit/16f6508c2928972be2a9f9001ea4ad9cf36bf8b0>`_
- Mark this test really as skipping. `b59d1ff05 <https://github.com/toscawidgets/tw2.core/commit/b59d1ff05c944257a8ab1a5cc27e40bb8435b07e>`_
- Skip tests on weird kajiki behavior.... `11285aa68 <https://github.com/toscawidgets/tw2.core/commit/11285aa680124438b4bd11617c34c0ee779f1eb2>`_
- Drop python-3.2 support since our deps dont support it. `0f777ea68 <https://github.com/toscawidgets/tw2.core/commit/0f777ea68079b3cec51e0f64b0b5fa8c8c6a06f0>`_
- Kill kajiki. `ea14b79f1 <https://github.com/toscawidgets/tw2.core/commit/ea14b79f199f527904ee87a8f0227039b04e0f7a>`_
- Merge pull request #94 from toscawidgets/feature/yielding-again `30e4c4b3d <https://github.com/toscawidgets/tw2.core/commit/30e4c4b3d1bdda1a04c72b857cf24dbc1d6297cc>`_
- Metadata fixups, #90 `38e306f88 <https://github.com/toscawidgets/tw2.core/commit/38e306f88f6528216d6437b0f905a82f0060b8a5>`_
- Imported doc fragments from tw2.forms `894b28540 <https://github.com/toscawidgets/tw2.core/commit/894b285407f7548d3a145b999aed40a4ce7283e5>`_

2.2.0.1
-------

- Provide more info in this traceback. `77efa240f <https://github.com/toscawidgets/tw2.core/commit/77efa240f601d0859a19ee6f9796c1e0d69acb0b>`_
- Variable, not Param. `03991510e <https://github.com/toscawidgets/tw2.core/commit/03991510ed7c3b5bbfdf188c70d093cdfd7ffefc>`_
- Update TG2 tutorial to current state of affairs `cb481999a <https://github.com/toscawidgets/tw2.core/commit/cb481999a9a696369fd33115b29a7114d3086d72>`_
- Make some things non-required that were newly required. `14507319d <https://github.com/toscawidgets/tw2.core/commit/14507319dabd84ec6175232c15551709623f7f48>`_
- Merge branch 'develop' of github.com:toscawidgets/tw2.core into develop `f5a00e83d <https://github.com/toscawidgets/tw2.core/commit/f5a00e83d6c02aa22f27cb177bd47cd2b6b82110>`_

2.2.0
-----

- Support more webob versions.  Fixes #77 `e071e9d33 <https://github.com/toscawidgets/tw2.core/commit/e071e9d3386c7d73ce6037ba7fac7ff0527b1f5b>`_
- Constrain webtest version for py2.5. `1214057c1 <https://github.com/toscawidgets/tw2.core/commit/1214057c1e00f896fc7d2c2f48b662325199a127>`_
- Port to python2/python3 codebase. `c1d2b7721 <https://github.com/toscawidgets/tw2.core/commit/c1d2b772163d13b310ffaccc6a9453290e3e447e>`_
- Travis-CI config update. `21a35d470 <https://github.com/toscawidgets/tw2.core/commit/21a35d4706f4f101aee22283489a6216a017fe54>`_
- Some py3 fixes for tw2.forms. `c82fb090f <https://github.com/toscawidgets/tw2.core/commit/c82fb090fde1ced3b9ad0e8befb5ae1516f1230c>`_
- @moschlar on the ball. `8b5cdcb81 <https://github.com/toscawidgets/tw2.core/commit/8b5cdcb813a99789ce560ef71fae4e68de35d314>`_
- Some setup for a port of tw2.devtools to gearbox. `08fd64a11 <https://github.com/toscawidgets/tw2.core/commit/08fd64a110449f87dab83c09e091fa5c04c95186>`_
- Merge branch 'feature/2.2' into develop `4aef579c7 <https://github.com/toscawidgets/tw2.core/commit/4aef579c77c62229d9f23c0018cfdeec73311514>`_
- Mention tw2.core.DirLink in the docs.  Fixes #69. `dce1db697 <https://github.com/toscawidgets/tw2.core/commit/dce1db6979d3c3abfae5ca10f05ad536b5a3347d>`_
- Reference gearbox tw2.browser in the docs. `2562933ee <https://github.com/toscawidgets/tw2.core/commit/2562933ee6868451fe7de8d65f8ad6f6b01034be>`_
- Include translations in distribution. `2791169fa <https://github.com/toscawidgets/tw2.core/commit/2791169fa7a5d69e7c46ca2cdbf545e24d0752fb>`_
- Merge pull request #82 from Cito/develop `f6d1f0502 <https://github.com/toscawidgets/tw2.core/commit/f6d1f0502b2463ada4bf43c34b2671bc3fa7ce22>`_
- Fix #84 in archive_tw2_resources `02eec525f <https://github.com/toscawidgets/tw2.core/commit/02eec525f83077d4bb1541e67c9ca5e40a971f1b>`_
- Merge pull request #85 from toscawidgets/feature/archive_tw2_resources `8791c3236 <https://github.com/toscawidgets/tw2.core/commit/8791c323653f177eff95c9abcb00cd37e9b76a56>`_
- Add a failing test for #25. `5d7b43a9f <https://github.com/toscawidgets/tw2.core/commit/5d7b43a9f41f7ae2b4f9a7d54792734ddbccdf49>`_
- Automatically assign widgets an ID. `ca81db016 <https://github.com/toscawidgets/tw2.core/commit/ca81db016c06583e37f573c8bec815e7c084dc1a>`_
- Enforce twc.Required (for #25). `94e61ec52 <https://github.com/toscawidgets/tw2.core/commit/94e61ec529a6ca04581435c1d579e05f5bf8b058>`_
- Deal with faulout from the twc.Required enforcement. `b5063a3c7 <https://github.com/toscawidgets/tw2.core/commit/b5063a3c72b01f4ffd06bd4eec2f11e162ec4c35>`_
- Merge pull request #87 from toscawidgets/feature/twc.Required `5add35cb9 <https://github.com/toscawidgets/tw2.core/commit/5add35cb9fb1a9e10dab0f5fe37faf4fbf42eca9>`_
- Method generators are not supported in unittest.TestCase subclasses. `30cb85826 <https://github.com/toscawidgets/tw2.core/commit/30cb8582692b64f75a22bfe62c89e58db49b9dae>`_
- Support if_empty and let BoolValidator validate None to False. `a9d48944a <https://github.com/toscawidgets/tw2.core/commit/a9d48944a8aa70e2d162b85a154b314fe33c3c8e>`_
- Merge pull request #88 from Cito/develop `2416cefb8 <https://github.com/toscawidgets/tw2.core/commit/2416cefb82ee7805308c61af2bcb4d179a3d0c7c>`_
- Merge branch 'hotfix/2.1.6' `a699822e5 <https://github.com/toscawidgets/tw2.core/commit/a699822e56031a1a0aa351f7bae19ff58401af18>`_
- Merge branch 'hotfix/2.1.6' into develop `dc99409b9 <https://github.com/toscawidgets/tw2.core/commit/dc99409b970a477a3b2c75096bbf536600a61448>`_
- Remove the spec file.  Fedora has it now. `004c3eda6 <https://github.com/toscawidgets/tw2.core/commit/004c3eda654a100925bab18df09985fdcf7406bc>`_

2.1.6
-----

- Fix #84 in archive_tw2_resources `65493f6ab <https://github.com/toscawidgets/tw2.core/commit/65493f6ab07b20dc05f1559f6744ac05b688c851>`_
- Support if_empty and let BoolValidator validate None to False. `4008ee77d <https://github.com/toscawidgets/tw2.core/commit/4008ee77de53a797fcb336c8643dc9a4b6c4a017>`_
- 2.1.6 `146d17261 <https://github.com/toscawidgets/tw2.core/commit/146d17261fd03c898f53b13300e30b37f642ac16>`_

2.1.5
-----

- Make sure future-queued resources make it into the middleware. `adb4aec79 <https://github.com/toscawidgets/tw2.core/commit/adb4aec7922f68a11c726629bc916d6968b3cecc>`_

2.1.4
-----

- Simplify the validator API and make it compatible with FormEncode. `5e5f91afa <https://github.com/toscawidgets/tw2.core/commit/5e5f91afabdef0e54d585acaec2c10f40773f765>`_
- Merge pull request #75 from Cito/develop `eb74470c6 <https://github.com/toscawidgets/tw2.core/commit/eb74470c69546eb5e4ae9576cbb60e340b520a8e>`_

2.1.3
-----

- Validation docs. `4132ff5f6 <https://github.com/toscawidgets/tw2.core/commit/4132ff5f631794579590499512b14eb0412a6c39>`_
- Typo fix.  Thanks Daniel Lepage. `0fbed935c <https://github.com/toscawidgets/tw2.core/commit/0fbed935c39a38da5046ea4f37f1861bca1c88c1>`_
- Fixes to tests busted by the introduction of CSSSource. `b795f3f2b <https://github.com/toscawidgets/tw2.core/commit/b795f3f2b68964d5d40908fc3004e4443274213d>`_
- More descriptive ParameterError for invalid ids. `6c06384ff <https://github.com/toscawidgets/tw2.core/commit/6c06384ff72e306029bcef3f8cdde00e7b833690>`_
- Windows support for resource serving. `0b939179a <https://github.com/toscawidgets/tw2.core/commit/0b939179abbd18eca7987ae6b31ad21e39c9a3d0>`_
- Added a half-done test of the chained js feature. `fe6924f89 <https://github.com/toscawidgets/tw2.core/commit/fe6924f896e64c6244551b47728a91c512dc16ee>`_
- We won't actually deprecate tw1-style calling. `f63a37c51 <https://github.com/toscawidgets/tw2.core/commit/f63a37c51a27ef1324125d02559a0680f89af9d5>`_
- Merge branch 'develop' into feature/chained-js-calls `c5e3f6a1f <https://github.com/toscawidgets/tw2.core/commit/c5e3f6a1fb781e85648ba78f6ef09d7a81fa01da>`_
- Added class_or_instance properties `fb9211eb0 <https://github.com/toscawidgets/tw2.core/commit/fb9211eb09f055b336d1a6d3f32c590043a20536>`_
- Revert "Added class_or_instance properties" `25df3bd3a <https://github.com/toscawidgets/tw2.core/commit/25df3bd3a06dafb6d42ebed4cde0b7c3733932dc>`_
- Chaining js calls are back in action. `eb7ef5056 <https://github.com/toscawidgets/tw2.core/commit/eb7ef5056f00b6f143e36d57a75d1269271f5737>`_
- Merge branch 'feature/chained-js-calls' into develop `612d52a88 <https://github.com/toscawidgets/tw2.core/commit/612d52a88e1c8128615b70a43afe90d370a4d3d6>`_
- Version for 2.0.0. `03f6d1280 <https://github.com/toscawidgets/tw2.core/commit/03f6d1280a17dae3ac2c0f7a33856d65fa0954b2>`_
- Forgot the damn classifier. `a780af954 <https://github.com/toscawidgets/tw2.core/commit/a780af954ff1279a840c204ea3212d14567d50cb>`_
- Merge branch 'hotfix/classifier' `df2556fec <https://github.com/toscawidgets/tw2.core/commit/df2556fec9f3ab0ec324ce2184e3f65c067ffc0b>`_
- Merge branch 'hotfix/classifier' into develop `22b667946 <https://github.com/toscawidgets/tw2.core/commit/22b667946d6a7fa3ca71d243cffaee4c18463fb0>`_
- Add coverage to the standard test process. `99400078e <https://github.com/toscawidgets/tw2.core/commit/99400078e7d13888951c3d9ca51a343a927ed991>`_
- When widgets have key they should be validated by key and not be id `edc575014 <https://github.com/toscawidgets/tw2.core/commit/edc5750145fe1e939208daaf4eef6c834d100c92>`_
- Re-added ancient/missing js_function __str__ behavior discovered in the bowels of moksha. `1d45fe424 <https://github.com/toscawidgets/tw2.core/commit/1d45fe4242d9db17cce8773676f2b77675e8e1d5>`_
- Demoted queued registration messages from "info" to "debug". `be23347d1 <https://github.com/toscawidgets/tw2.core/commit/be23347d104623355b3664296e11fb0d5c72bd5d>`_
- Clutch simplejson hacking. `fb7c06b66 <https://github.com/toscawidgets/tw2.core/commit/fb7c06b661fa57cb0fe24a0f9d6f82dc987e1a5d>`_
- Encoding widgets works again. `07fb3c94b <https://github.com/toscawidgets/tw2.core/commit/07fb3c94b2eb9b52066bb47c883e57041df6847a>`_
- More PEP8. `b387fa470 <https://github.com/toscawidgets/tw2.core/commit/b387fa47025c4d09ba8c28bce7895215ac5b417d>`_
- Found the killer test. `d81926c5a <https://github.com/toscawidgets/tw2.core/commit/d81926c5a1108079e5a2525e456ad6a077c776d9>`_
- Update to that test. `152650597 <https://github.com/toscawidgets/tw2.core/commit/152650597568ce0040fef9442cdb69cda38a899b>`_
- A stab at handling function composition.  Tests pass. `7ae78e03b <https://github.com/toscawidgets/tw2.core/commit/7ae78e03bd791f85d447fc0e3f6b7a6f4f392f74>`_
- This is clearly unsustainable. `c96fb2898 <https://github.com/toscawidgets/tw2.core/commit/c96fb28988f596da3253c25ed8f17527cb9141ca>`_
- Solve the function composition problem. `ff432f26a <https://github.com/toscawidgets/tw2.core/commit/ff432f26a5c0656c17b85a5d4ef57a8050e93ede>`_
- Merge branch 'feature/function-composition' into develop `5f46d5069 <https://github.com/toscawidgets/tw2.core/commit/5f46d506935c1ca9f97923d25b22ae89a9098fcb>`_
- Some comments in the encoder initialization. `a479c7aa5 <https://github.com/toscawidgets/tw2.core/commit/a479c7aa54bddac443922d05e0cd3c9699e6b1de>`_
- The output of this test changes depending on what other libs are installed. `1b4306160 <https://github.com/toscawidgets/tw2.core/commit/1b4306160dd68898aab617cc2f5c373f1116bea1>`_
- Abstracted ResourceBundle out of Resource for tw2.jqplugins.ui. `56a6ba35a <https://github.com/toscawidgets/tw2.core/commit/56a6ba35abdc51b9f48f17385fc5e55c4463260b>`_
- When widget has key and so gets data by key validation was still returning data by id. Now validation returns data by key when available. Also simplify CompoundWidget validation `fa197ba30 <https://github.com/toscawidgets/tw2.core/commit/fa197ba30ace8540786f0ea79502074e5c66c15b>`_
- Cover only the tw2.core package `75001ec74 <https://github.com/toscawidgets/tw2.core/commit/75001ec74fafd35dee012ca3f5b7603b6288768a>`_
- Fix regression in tw2.sqla. `f6089fd7f <https://github.com/toscawidgets/tw2.core/commit/f6089fd7f0caff96063ffb72a67556ca8f7d333a>`_
- Revert CompoundValidation tweak.  Works with tw2.sqla now.  Fixes #9. `032994731 <https://github.com/toscawidgets/tw2.core/commit/0329947311d9538ac0f299fcfbe87cb1f20dc477>`_
- Added a test case for amol's validation situation. `06ac1b3fb <https://github.com/toscawidgets/tw2.core/commit/06ac1b3fb78a5c2c7187e8556adc6a42836f5eba>`_
- Supress top-level validator messages if they also apply messages to compound widget children. `c144b01f3 <https://github.com/toscawidgets/tw2.core/commit/c144b01f3dd6d4b3e9a61da5e647fd9946c2e11c>`_
- Correctly supress top-level validator messages. `8b15822e1 <https://github.com/toscawidgets/tw2.core/commit/8b15822e1ad6c29ff6f1d4ca31c4bd1db3da2aae>`_
- Write test to better test CompoundWidget error reporting `74dd87075 <https://github.com/toscawidgets/tw2.core/commit/74dd87075b5e3f82ce9c9fb4768326bdf4484d8d>`_
- Handle unspecified childerror case uncovered by latest test. `e94c80341 <https://github.com/toscawidgets/tw2.core/commit/e94c8034173c461074f4d2364d32f8f3dc3ee871>`_
- Differentiated test names. `5a7ef40cc <https://github.com/toscawidgets/tw2.core/commit/5a7ef40cc09934b95d0d2e31cc5ab751774f7b22>`_
- Compatibility with dreadpiratebob and percious's tree. `af7a2e6b8 <https://github.com/toscawidgets/tw2.core/commit/af7a2e6b867bca63b09b5be90f2ca01bfb506f4b>`_
- Avoid receiving None instead of the object itself when object evaluates to False `e8c513c3a <https://github.com/toscawidgets/tw2.core/commit/e8c513c3a7b9b3a753937b69cae80b790dde90f1>`_
- 2.0.1 release. `c056c88f6 <https://github.com/toscawidgets/tw2.core/commit/c056c88f6b2627c2ed0bdd07026508580da0ea2e>`_
- Initial RPM spec. `12cec0ed8 <https://github.com/toscawidgets/tw2.core/commit/12cec0ed8f656b3da5167953cffe4fffe2191596>`_
- Rename. `5ebc78d87 <https://github.com/toscawidgets/tw2.core/commit/5ebc78d87b08f6a3f855b35aa4ff3ef02b162b1b>`_
- Removed changelog.  It's from the way back tw1 days. `eb5fdcc65 <https://github.com/toscawidgets/tw2.core/commit/eb5fdcc6565726a119187571114c8b89dba9b058>`_
- Skipping tests that rely on tw2.forms and yuicompressor. `c7ae7984a <https://github.com/toscawidgets/tw2.core/commit/c7ae7984abfb3c6f503ebd98e72463a81d286d2c>`_
- We don't actually require weberror. `7b269e77e <https://github.com/toscawidgets/tw2.core/commit/7b269e77e3fffb39d571106a0c787e133a813a9a>`_
- Include test data for koji builds. `3f61860d3 <https://github.com/toscawidgets/tw2.core/commit/3f61860d34abeff824d98bb4395a26c50545d9b6>`_
- First iteration of the new rpm.  It actually built in koji. `6b924cdda <https://github.com/toscawidgets/tw2.core/commit/6b924cdda03d134f728721a9424ade88bd853336>`_
- exception value wasn't required and breaks compatibility with Python2.5 `de857ce6e <https://github.com/toscawidgets/tw2.core/commit/de857ce6ed4b15eeadb0433cc6ede63464dd0bcf>`_
- Merge pull request #16 from amol-/develop `0e9faf439 <https://github.com/toscawidgets/tw2.core/commit/0e9faf4393b29a4b3c8f34b3f1fd041a02f7c129>`_
- More Py2.5 compat. `057ac45bb <https://github.com/toscawidgets/tw2.core/commit/057ac45bbba01ebd1e38144108445cd36efe11d2>`_
- 2.0.2 release with py2.5 bugfixes for TG. `bd8304957 <https://github.com/toscawidgets/tw2.core/commit/bd830495770f95f4d0bfdfb21a98662d15f7ab30>`_
- Specfile update for 2.0.2. `d9aeb76b3 <https://github.com/toscawidgets/tw2.core/commit/d9aeb76b31687b516a2f4871a52bc70bb8500e27>`_
- Changed executable bit for files that should/shouldn\'t have it. `4d77e3043 <https://github.com/toscawidgets/tw2.core/commit/4d77e30437be3d66aa5af9f1671d802b51e85654>`_
- Exclude *.pyc files from template directories. `4d281c684 <https://github.com/toscawidgets/tw2.core/commit/4d281c6840edee64a58bfd4b3d17ba3f8ab92a7d>`_
- Version bump for rpm fixes. `a76db4c94 <https://github.com/toscawidgets/tw2.core/commit/a76db4c942c7eeb353d02086f3b0489f64ade1bb>`_
- Remove pyc files from the sdist package.  Weird. `da3ddaea1 <https://github.com/toscawidgets/tw2.core/commit/da3ddaea1a0049168a673739a87711e0c3e4fceb>`_
- Switched links in the doc from old blog to new blog. `8f7332fd1 <https://github.com/toscawidgets/tw2.core/commit/8f7332fd150d330ef9040fe7bf1309560ebfe23f>`_
- Be more careful with the multiprocessing,logging import hack. `a8857267e <https://github.com/toscawidgets/tw2.core/commit/a8857267e6c682fdb770b8a9d72f2de47c6fab92>`_
- Compatibility with older versions of simplejson. `64d16f234 <https://github.com/toscawidgets/tw2.core/commit/64d16f234f8aec46a23d4a92e9da53e5e8c77a87>`_
- Test suite fixes on py2.6. `e37b7e1c6 <https://github.com/toscawidgets/tw2.core/commit/e37b7e1c6dc20bd155d59060a170a90e7d8eb204>`_
- 2.0.4 with improved py2.6 support. `7b6784e1d <https://github.com/toscawidgets/tw2.core/commit/7b6784e1df26079ca4e154d7bf5160f87d09f9b3>`_
- A little more succint in the middleware. `5cc582cd9 <https://github.com/toscawidgets/tw2.core/commit/5cc582cd9e53cf0536ea992eec85a7c208ae068c>`_
- Allow streaming html responses to pass through the middleware untouched. `3f4a5a4b9 <https://github.com/toscawidgets/tw2.core/commit/3f4a5a4b91bbea9534760d7ea3497fea0513e157>`_
- Simple formatting in the spec. `d7020a9fa <https://github.com/toscawidgets/tw2.core/commit/d7020a9fae23cdd0c7bdf7edd8cbaa7b3fb779d2>`_
- Version bump. `48768720b <https://github.com/toscawidgets/tw2.core/commit/48768720bd5488b70116a96cbe02fad2f9eefaf4>`_
- Stripped out explicit references to kid and cheetah. `595ba7c6c <https://github.com/toscawidgets/tw2.core/commit/595ba7c6c84e5f8201760dc96eb71b5fc8bb4058>`_
- Removed unused reference to reset_engine_name_cache. `0e4c40e64 <https://github.com/toscawidgets/tw2.core/commit/0e4c40e6491783149beb7d82e0cbd092b7248dae>`_
- Removed unnecessary "reset_engine_name_cache" `2b3ed27a7 <https://github.com/toscawidgets/tw2.core/commit/2b3ed27a7b629e997b0c48c5d7354aed181fb0b8>`_
- Removed a few leftover references to kid. `1755fd14a <https://github.com/toscawidgets/tw2.core/commit/1755fd14aac5691d1688a89ad97e56b2ac7f081e>`_
- More appropriate variable name. `1c27c620a <https://github.com/toscawidgets/tw2.core/commit/1c27c620a55c2db67abaf351716c1cf1fe30cc6f>`_
- First rewrite of templating system. `283367bb8 <https://github.com/toscawidgets/tw2.core/commit/283367bb8d0ffb54b723351862069092085b6345>`_
- Template caching. `4d16358e0 <https://github.com/toscawidgets/tw2.core/commit/4d16358e0a58b9d83e8e0abd8a4f364fda8ca2fe>`_
- First stab at jinja2 support. `17d17234a <https://github.com/toscawidgets/tw2.core/commit/17d17234ac00d12aad6e4c4de1e5a3a9f1e06469>`_
- Update to the docs. `e9658290b <https://github.com/toscawidgets/tw2.core/commit/e9658290beebe5792cf52f3b00c4adaf24eb6920>`_
- Massive dos2unix pass.  For good health. `e74bbc42b <https://github.com/toscawidgets/tw2.core/commit/e74bbc42bec3378e79d279b2d1a2d1c9682ee8fa>`_
- PEP8. `62d256c4d <https://github.com/toscawidgets/tw2.core/commit/62d256c4d3b44f0f8dc206f8dada86762dc1e477>`_
- Reference email thread regarding "displays_on" `25ffcd339 <https://github.com/toscawidgets/tw2.core/commit/25ffcd33943d132308ffaa6dfea1a24ea7e7bf12>`_
- Added support for kajiki. `f809d1a5d <https://github.com/toscawidgets/tw2.core/commit/f809d1a5dbee8b45e624b5c954356df1b9116df9>`_
- Default templates for kajiki and jinja. `9a170d3cb <https://github.com/toscawidgets/tw2.core/commit/9a170d3cb51e071fc3fcb1de4aeec86aa9f18d97>`_
- More robust testing of new templates. `55f1fbe0a <https://github.com/toscawidgets/tw2.core/commit/55f1fbe0a6a49bff25514cf40c7149fae43eb513>`_
- Pass filename to mako templates for easier debugging. `5e63adcbe <https://github.com/toscawidgets/tw2.core/commit/5e63adcbed071464ef0b10096a3338600561886b>`_
- More correct dotted template loading. `07b67c84d <https://github.com/toscawidgets/tw2.core/commit/07b67c84dae7d181f4e0fe24a5fe8a3423c1b6ae>`_
- Added support for chameleon. `fa8c160d4 <https://github.com/toscawidgets/tw2.core/commit/fa8c160d4e8d8c3ab33d8433446197774730a8e2>`_
- Default chameleon templates. `69de63cf6 <https://github.com/toscawidgets/tw2.core/commit/69de63cf6f9d29a8431936879b7b3b60cb46dc1b>`_
- Updated docs with kajiki and chameleon. `ef291ce4a <https://github.com/toscawidgets/tw2.core/commit/ef291ce4a7cd353ea1be85faed0340c06d8423e2>`_
- Added three tests for http://bit.ly/KNYAxq `0e775ab1e <https://github.com/toscawidgets/tw2.core/commit/0e775ab1ea81d09417e502585f452392e4646a3c>`_
- Resurrecting the smarter logic of the "other" tw encoder.  Hurray for git history. `1379196d3 <https://github.com/toscawidgets/tw2.core/commit/1379196d338e801c04080a63843ab138077683b6>`_
- Added test for #12.  Passes. `b6bbf92a4 <https://github.com/toscawidgets/tw2.core/commit/b6bbf92a4ff87135dcc2a4af23b0bef7e677a125>`_
- Use __name__ in tests. `fbe2b6979 <https://github.com/toscawidgets/tw2.core/commit/fbe2b697930e6a8ff9a124a4aab27ba34e7c3def>`_
- Added failing test for Issue #18. `e962a03fb <https://github.com/toscawidgets/tw2.core/commit/e962a03fbe15f830bd10e276b7ad3d5c4bac9ee3>`_
- Merge pull request #21 from toscawidgets/feature/multiline-js `c9e0ada6f <https://github.com/toscawidgets/tw2.core/commit/c9e0ada6f2bb8955c2320dc873abb0adae35f186>`_
- Merge branch 'develop' into feature/template-sys `b32a024c3 <https://github.com/toscawidgets/tw2.core/commit/b32a024c3d023237fade1b78e0553ee7960bfc33>`_
- Merge branch 'develop' into feature/issue-18 `5b1c1dadf <https://github.com/toscawidgets/tw2.core/commit/5b1c1dadf66ea298a08b6c1072c7e2ff3eb7e8eb>`_
- Guess modname in post_define.  Fixes #18. `d3d2aeb35 <https://github.com/toscawidgets/tw2.core/commit/d3d2aeb35a973e75c947ff9ecae9d9350b51ea60>`_
- Merge branch 'feature/issue-18' into develop `4f0d496fc <https://github.com/toscawidgets/tw2.core/commit/4f0d496fc671d06bc0b0aceab2625e2e8360eb88>`_
- Version bump - 2.0.6. `ea7637a20 <https://github.com/toscawidgets/tw2.core/commit/ea7637a20c422c91e0454040d48af1e6182aad4b>`_
- Don't check for 'not value' in base to_python.  Messes up on cgi.FieldStorage. `204e20fbd <https://github.com/toscawidgets/tw2.core/commit/204e20fbdec27672547f26b19f0fc3eccbee3df0>`_
- Added a note to the docs about altering JSLink links.  Fixes #15. `28e458fe4 <https://github.com/toscawidgets/tw2.core/commit/28e458fe448466631848fcacba35be467dab7e27>`_
- dos2unix pass on the docs/ folder. `ce4f813e7 <https://github.com/toscawidgets/tw2.core/commit/ce4f813e72449abca9b205b21143fae452c52cd1>`_
- Typo fix. `34fee8fa9 <https://github.com/toscawidgets/tw2.core/commit/34fee8fa9095b00614a94e21b99e5cf46484ae25>`_
- Trying out travis-ci. `8e9414ae0 <https://github.com/toscawidgets/tw2.core/commit/8e9414ae081e62ee191ad9e2783c149f5583fa97>`_
- Trying out travis-ci. `abc5b4161 <https://github.com/toscawidgets/tw2.core/commit/abc5b41611756e64b7661a4b2df6fe1d93bc19e2>`_
- Updates for testing on py2.5 and py2.6. `56ce437ef <https://github.com/toscawidgets/tw2.core/commit/56ce437ef3ffac6aa33a92b4c56c3186ebc10b84>`_
- Merge branch 'develop' `0f4b81113 <https://github.com/toscawidgets/tw2.core/commit/0f4b81113b7d24cd795888ee01d67ba973bf9e8a>`_
- Added build table to the README. `4da336497 <https://github.com/toscawidgets/tw2.core/commit/4da3364971f0c76604c595ae4e840f474633d06f>`_
- Merge branch 'develop' into feature/template-sys `832435945 <https://github.com/toscawidgets/tw2.core/commit/832435945ffcdcb5608225d38e7262d09c16ce01>`_
- Python2.5 support. `66e93b66d <https://github.com/toscawidgets/tw2.core/commit/66e93b66d89a8670d4763560eb34ade94e15195c>`_
- JS and CSSSource require a .src attr. `ca02d9713 <https://github.com/toscawidgets/tw2.core/commit/ca02d9713caeb773179b4163eedc07f8fe6775d3>`_
- Use mirrors for travis. `b504714da <https://github.com/toscawidgets/tw2.core/commit/b504714da536dc7e1603349b7c987989485a1a77>`_
- Revert "Use mirrors for travis." `9fc882050 <https://github.com/toscawidgets/tw2.core/commit/9fc8820509518b6af112c69dea3a9c5e70a13c15>`_
- Fixed mako and genshi problems in new templating system found by testing against tw2.devtools. `41b8e5264 <https://github.com/toscawidgets/tw2.core/commit/41b8e52649683333857dbf36bef583c9ae57b736>`_
- Version bump -- 2.1.0a ft. templating system rewrite. `c89009332 <https://github.com/toscawidgets/tw2.core/commit/c890093324aef0df7b5ffc47f1c74cab2063dd05>`_
- Ship new templates with the source dist. `2fb6cf8da <https://github.com/toscawidgets/tw2.core/commit/2fb6cf8dadef8ca890fabf9b3b5445c6d1c9e51c>`_
- Attribute filename for jinja and kajiki. `d130c3c9f <https://github.com/toscawidgets/tw2.core/commit/d130c3c9f17e13984bc9d28d3601dcfdfa5f6ca6>`_
- Provide an option for WidgetTest to exclude engines. `c822b2a66 <https://github.com/toscawidgets/tw2.core/commit/c822b2a6699c98a87bf7dbe9510d7709c023b5d0>`_
- 2.1.0a4 - Fix bug in automatic resource registration. `efcd51724 <https://github.com/toscawidgets/tw2.core/commit/efcd51724cb4bd7360ece576d9cc195c442c8944>`_
- Support template inheritance at Rene van Paassen's request. `fc58e929a <https://github.com/toscawidgets/tw2.core/commit/fc58e929ac6cd04eb3bb698eff9249f97b85d31c>`_
- Version bump for template inheritance. `6b6658870 <https://github.com/toscawidgets/tw2.core/commit/6b6658870485299cde517788b59e3917cf25666e>`_
- Fix required Keyword for Date*Validators `14196d9ce <https://github.com/toscawidgets/tw2.core/commit/14196d9ce4a3e427c9d5e07073f695acf2d074c4>`_
- Bridge the tw2/formencode API divide. `547357c7f <https://github.com/toscawidgets/tw2.core/commit/547357c7fa9bc51dc7e8d47d44bbc4d56f1372af>`_
- Make rendering_extension_lookup propagate up to templating layer `8d89dabd8 <https://github.com/toscawidgets/tw2.core/commit/8d89dabd8a675c6d6e7d677588f436dab38048ee>`_
- Added test for #30.  Oddly, it passes `7d1d83852 <https://github.com/toscawidgets/tw2.core/commit/7d1d83852d4790c1b2c17ee03941e7dbb1faeb9a>`_
- Trying even harder to test #30. `b66b59ff5 <https://github.com/toscawidgets/tw2.core/commit/b66b59ff512b70e0bb4237bf14c85898d0626bb1>`_
- Version bump to 2.1.0b1. `3483107a6 <https://github.com/toscawidgets/tw2.core/commit/3483107a6320fca2595c76ecff60be9762318649>`_
- Puny py2.5 has no context managers. `cb1e821c8 <https://github.com/toscawidgets/tw2.core/commit/cb1e821c87e8b44d9da7c52c9e0812d8b391d048>`_
- PEP8.  Cosmetic. `50d88cc93 <https://github.com/toscawidgets/tw2.core/commit/50d88cc9326b470326d04b7983f81e3982338662>`_
- Future-proofing.  @amol- is a rockstar. `bb006dfeb <https://github.com/toscawidgets/tw2.core/commit/bb006dfeb5107fb3fb1e43eb5128c205d1b3867b>`_
- Conform with formencode.  Fixes #28. `f3bf2a821 <https://github.com/toscawidgets/tw2.core/commit/f3bf2a821e1f9f7730e8ea8441918d063d1a5025>`_
- Improve handling of template path names under Windows. `e2bbeb29c <https://github.com/toscawidgets/tw2.core/commit/e2bbeb29ce6c193bb319a129a83616585484adb1>`_
- Borrowed backport of os.path.relpath for py2.5.  Related to #30. `f29337629 <https://github.com/toscawidgets/tw2.core/commit/f293376292ad703d9860c242d965535c28a76ac4>`_
- Whoops.  Forgot to use the new relpath.  #30. `f308bef92 <https://github.com/toscawidgets/tw2.core/commit/f308bef9232817c1edf072c8370ef823e5a481da>`_
- Use util.relpath instead of os.path.relpath. `3c302eaac <https://github.com/toscawidgets/tw2.core/commit/3c302eaac3c4eac565138be652d5be3e60c64421>`_
- .req() returns the validated widget is one exists. `be8f39404 <https://github.com/toscawidgets/tw2.core/commit/be8f39404c585f44ffb9333e1aa0f2e82ee951e5>`_
- Use **kw even when pulling in the validated widget. `f78492be9 <https://github.com/toscawidgets/tw2.core/commit/f78492be9406335cead45da79e429ffbf48efdce>`_
- Trying to duplicate an issue with Deferred. `cefbbfd73 <https://github.com/toscawidgets/tw2.core/commit/cefbbfd739c1b803039a9dded72098db8fc540b3>`_
- Tests for #41. `7c61047b9 <https://github.com/toscawidgets/tw2.core/commit/7c61047b9585e0f4a584a4c7389d213f2f3a24d4>`_
- Handle arguments to display() called as instance method. `86894492d <https://github.com/toscawidgets/tw2.core/commit/86894492d5c1565c7d49747bde8f5c848dbc9b61>`_
- Cosmetic. `b94180f25 <https://github.com/toscawidgets/tw2.core/commit/b94180f25b41f4f6c73a115bc6456c4f23b4ce6c>`_
- Found the failing test for @amol-'s case. `284c66a38 <https://github.com/toscawidgets/tw2.core/commit/284c66a386a4cb76c351ec6b6dd21fcf229080e3>`_
- Allow Deferred as kwarg to .display(). `d4c6dcfc6 <https://github.com/toscawidgets/tw2.core/commit/d4c6dcfc68d46e7dc6c384ee0524d1fdce951aa2>`_
- Second beta 2.1.0b2 to verify some bugfixes. `b6ff67ab7 <https://github.com/toscawidgets/tw2.core/commit/b6ff67ab72fd3ac8dd7544af98b66ee83bd27413>`_
- Failing test for Deferred. `d26389d13 <https://github.com/toscawidgets/tw2.core/commit/d26389d13e498a90ba625189c41e79e932244b48>`_
- @amol-'s fix for the Deferred subclassing problem. `c08c0508b <https://github.com/toscawidgets/tw2.core/commit/c08c0508b07643fc0e1bbf99f5a7a9866e05edc3>`_
- 2.1.0. `725fd6aba <https://github.com/toscawidgets/tw2.core/commit/725fd6aba59553222d7e7ca1be34ba27ae5f4f43>`_
- Fixup copyright date `bc509ca66 <https://github.com/toscawidgets/tw2.core/commit/bc509ca66c861c16702efa4990067d93e63c1dd3>`_
- avoid issues with unicode error messages `b5a314de7 <https://github.com/toscawidgets/tw2.core/commit/b5a314de760e3e4809cc0056ab4af2422e71a775>`_
- Link to rtfd from README. `1269dff73 <https://github.com/toscawidgets/tw2.core/commit/1269dff73c670150d5498b8707e1d2fa5233ffe4>`_
- Added jinja filter to take care of special case html bolean attributes such as radio checked} `da25dbfaf <https://github.com/toscawidgets/tw2.core/commit/da25dbfafda1a593aa01bc01a31ef1c1c7bfd89f>`_
- Added htmlbools filter to jinja templates `fb00eac66 <https://github.com/toscawidgets/tw2.core/commit/fb00eac669c5fca1fe177e054e503faabbd14a0a>`_
- Fixed corner case which produced harmless but incorrect output if the special case attribute value is False `38a4505b8 <https://github.com/toscawidgets/tw2.core/commit/38a4505b89b232b8283e675c514d040750b2e516>`_
- Merge pull request #48 from clsdaniel/develop `270784d5a <https://github.com/toscawidgets/tw2.core/commit/270784d5a339e2402a0cf5234e668028ed3a3a3f>`_
- Removed commented-out lines. `55af65d6c <https://github.com/toscawidgets/tw2.core/commit/55af65d6c95107450187be0df4e5c0bc65a9d0bd>`_
- 2.1.1 for jinja updates and misc bugfixes. `0ff5ffcd2 <https://github.com/toscawidgets/tw2.core/commit/0ff5ffcd26b731e511b6b51b250190f6de962cec>`_
- Since 2.0 autoescaping in widgets got lost due to new templates management `59f478fb5 <https://github.com/toscawidgets/tw2.core/commit/59f478fb5471e11bdc34903df69e924060616c5f>`_
- Mark attrs as Markup to avoid double escaping `5e138ace2 <https://github.com/toscawidgets/tw2.core/commit/5e138ace2c90cb07f09fb577f3f70e251a1deba2>`_
- Mark as already escape JSFuncCall too and update test to check the result for all the template engines `7c0c60ae2 <https://github.com/toscawidgets/tw2.core/commit/7c0c60ae24006e84f44f788224d08f7b68428759>`_
- Merge pull request #49 from amol-/develop `f6a3dda84 <https://github.com/toscawidgets/tw2.core/commit/f6a3dda8411307c990b2d62c2de040c92532985f>`_
- Add proper escaping for JS and CSS sources `af6d233df <https://github.com/toscawidgets/tw2.core/commit/af6d233dfa71bbf470d5e3e3f266a00978ba69f6>`_
- Merge pull request #50 from amol-/develop `e99f82879 <https://github.com/toscawidgets/tw2.core/commit/e99f82879532f012b43554bd4ad2784ba9702a3e>`_
- Provide a Widget compound_key make available a compound_key attribute which can be used by tw2.forms as the default value for FormField name argument `ee571a215 <https://github.com/toscawidgets/tw2.core/commit/ee571a215267de2da2b663e74417b7cb2509ecf0>`_
- Version bump, 2.1.2. `1b64e3f83 <https://github.com/toscawidgets/tw2.core/commit/1b64e3f836d6704661e8873f1213df78399c3d87>`_
- Allow inline templates with no markup. `de19fa2b3 <https://github.com/toscawidgets/tw2.core/commit/de19fa2b355c2dec46a520ab4e6e0682177f29cf>`_
- PEP8. `c2da40a1b <https://github.com/toscawidgets/tw2.core/commit/c2da40a1b528e6cc48ff2ae7b90ce67f831d0b9a>`_
- Test that reveals a bug in tw2.jqplugins. `6a88d0413 <https://github.com/toscawidgets/tw2.core/commit/6a88d0413a0ec4972cb72c0e22f36a23e9a7c3ae>`_
- Do not translate empty strings, this does not work. `e4f29829d <https://github.com/toscawidgets/tw2.core/commit/e4f29829d6362902b297bc841e753d1bd3c4c055>`_
- Merge pull request #53 from Cito/develop `168f2727f <https://github.com/toscawidgets/tw2.core/commit/168f2727f93a80ee832fe1d8bc0616ec44be0fe0>`_
- Add translations and passing lang via middleware `a10a14e26 <https://github.com/toscawidgets/tw2.core/commit/a10a14e260aa0f459d8586f4066c7c2519a2f58c>`_
- Merge pull request #59 from Cito/develop `cbf603238 <https://github.com/toscawidgets/tw2.core/commit/cbf603238ddc9b0f2b201fe5e5a927c8d65473ba>`_
- Inject CSS/JSSource only once. `ae13c369a <https://github.com/toscawidgets/tw2.core/commit/ae13c369a552cb71c1156a817412582f6454406f>`_
- Merge pull request #61 from Cito/develop `bb5c2a225 <https://github.com/toscawidgets/tw2.core/commit/bb5c2a225a739c7cf7434dcca20623a3bdef2f0b>`_
- Test blank validator for both None and empty string. `1167286c3 <https://github.com/toscawidgets/tw2.core/commit/1167286c392b6dc7e0a09972006c4b8ae5a36300>`_
- Add some more translations. `32374168d <https://github.com/toscawidgets/tw2.core/commit/32374168d79f00b15c59ff0696b6b3d238ab0f30>`_
- Merge pull request #64 from Cito/develop `50fc09a24 <https://github.com/toscawidgets/tw2.core/commit/50fc09a24d888d12e711f4ccda0e39b0bba1a7fe>`_
- Fix #63. `df2920d83 <https://github.com/toscawidgets/tw2.core/commit/df2920d83de2366993334f581744fede2877600b>`_
- Added a note about the add_call method to the design doc. `e901b1243 <https://github.com/toscawidgets/tw2.core/commit/e901b124342b73ad69cf5210fdb9dadd008d4d0a>`_
- Reference js_* docstrings from design doc.  Fixes #58. `55001c742 <https://github.com/toscawidgets/tw2.core/commit/55001c742bb3d3df56ef8d5eef806feac1c66869>`_
- General docs cleanup. `144d5cfbb <https://github.com/toscawidgets/tw2.core/commit/144d5cfbb63e85b37bb9786cdc6bd71f4a1f0e99>`_
- Fix broken links to tw2.core-docs-pyramid `14e5223e2 <https://github.com/toscawidgets/tw2.core/commit/14e5223e2b4e8c6a2f75060331b036a0ad34a799>`_
- Fix broken links to tw2.core-docs-turbogears `55a333b1c <https://github.com/toscawidgets/tw2.core/commit/55a333b1c6b2959e600d5d0ba99edcf582226919>`_
- Merge pull request #66 from lukasgraf/lg-doc-url-fixes `4d123d0b1 <https://github.com/toscawidgets/tw2.core/commit/4d123d0b1d6636c43d8cf3e6bbe6512f5954a012>`_
- provide compatibility with formencode validators `c382eed46 <https://github.com/toscawidgets/tw2.core/commit/c382eed46d8339ceb75440ed4d998abf1160a150>`_
- Merge pull request #71 from amol-/develop `65b9550ca <https://github.com/toscawidgets/tw2.core/commit/65b9550ca12c97df850bc7941de87501e5cb2346>`_
- Link to github bug tracker from docs.  Fixes #67. `f849b5d03 <https://github.com/toscawidgets/tw2.core/commit/f849b5d035206069399fef978eb3e4c02c63ea45>`_
- pass on state value in validation. `7c6791d80 <https://github.com/toscawidgets/tw2.core/commit/7c6791d802f854b8b1708e0928e24b889726989f>`_
- Updated pyramid docs.  Fixes #23. `9547108fb <https://github.com/toscawidgets/tw2.core/commit/9547108fbf90cc84983f9a069d0fedea83aa1c07>`_
- Don't let ``add_call`` pile-up new js resources. `f1d698c55 <https://github.com/toscawidgets/tw2.core/commit/f1d698c5500bb14799845c332e4fd81906e21949>`_
