## user
Does pygame use sdl3 yet
## assistant

As of April 2025, Pygame does not yet use SDL3. The mainline Pygame (version 2.6.1) continues to rely on SDL2. However, the Pygame Community Edition (pygame-ce) is actively working towards integrating SDL3 support for its upcoming 3.0.0 release.

The developers aim to fully support SDL3 features while maintaining compatibility with SDL2. This transition involves significant code refactoring to accommodate SDL3's changes and enhancements. The plan includes leveraging SDL3's new capabilities and making minor adjustments to the Pygame API to align with SDL3's architecture citeturn0search4turn0search0.

In the meantime, if you're interested in experimenting with SDL3 in Python, you might consider using PySDL3—a pure Python wrapper for SDL3. This library allows developers to access SDL3 functionalities directly in Python, independent of Pygame citeturn0search1.

For the latest updates on Pygame's transition to SDL3, you can follow the development progress on the pygame-ce GitHub repository. 
## user
How far along is the Pygame Community Edition in integrating SDL3 features?
## assistant
As of April 2025, the Pygame Community Edition (pygame-ce) is actively progressing toward integrating SDL3 support in its upcoming 3.0.0 release. However, this milestone is currently about 14% complete, indicating that full SDL3 integration is still in the early stages of development citeturn0search0.

The development team is working on refactoring the codebase to accommodate SDL3's architecture and features. This includes discussions on potential API changes to align with SDL3's capabilities, such as enhanced GPU performance and native shader support citeturn0search2.

Recent updates show that the project has incorporated the latest SDL3 libraries (e.g., SDL3 version 3.2.6) into its build system, which is a significant step toward full integration citeturn0search3.

While experimental modules like `pygame._sdl2` offer some SDL3 functionalities, they are still under development and subject to change citeturn0search7. Therefore, for production projects, it's advisable to continue using the stable SDL2-based versions of pygame-ce until SDL3 support is fully realized.

For the latest updates and to track the progress of SDL3 integration, you can follow the [pygame-ce GitHub repository](https://github.com/pygame-community/pygame-ce). 
## assistant
As of April 2025, the Pygame Community Edition (pygame-ce) is actively working towards integrating SDL3 support for its upcoming 3.0.0 release. The project has set a milestone for version 3.0.0, which is currently about 14% complete, with 12 open issues and 2 closed ones. citeturn0search1

Recent development activities indicate progress in this direction. For instance, on March 2, 2025, there were updates to bump SDL2 to version 2.32.2 and SDL3 to version 3.2.6, along with SDL3_ttf to 3.2.0. citeturn0search3 These updates suggest that the team is preparing the codebase to accommodate SDL3's features.

Discussions are ongoing regarding the API changes required for SDL3 integration. A GitHub issue titled "DISCUSSION: pygame-ce 3.0 API changes" has been opened to deliberate on the necessary modifications. citeturn0search2 This indicates that the team is considering how to adapt the existing API to align with SDL3's architecture.

While there is no official release date for pygame-ce 3.0.0 yet, the project's active development and recent updates suggest that integration with SDL3 is progressing steadily. For the latest updates, you can follow the development progress on the pygame-ce GitHub repository. 