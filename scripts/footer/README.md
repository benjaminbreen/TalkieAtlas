# Footer illustration selection

The footer draws three distinct names from every illustrated library entry,
including pair outcomes and custom robot filenames. The pool has no score cutoff
or entry cap. A shuffled deck persists in sessionStorage across page visits and
reloads in the same tab. Draws avoid the current entry and the immediately previous
trio; a new shuffle starts when the deck runs out. Without sessionStorage, fresh
random draws still work. No timed changes occur while reading.

The shared header also uses footer-personas.json; its existing filename filter
continues to choose canonical single-neuron robot images.

Source: scripts/footer/build_footer.py. Pool-only refresh avoids rewriting pages.
The source is maintained in the Talkie Harness workspace alongside site templates.
