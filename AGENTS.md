# Agent Instructions: Tide & Tackle

This project is a salmon-farming game. The open world, exploration, vehicles, and side activities support that core; they must not replace or obscure it.

## Product Priorities

- Keep salmon farming the primary gameplay loop: care for stock, manage feed and pen conditions, grow/re-stock cohorts, harvest fish, and deliver them to market.
- Model smolt production as salmon husbandry: fertilized eggs, incubation, alevin/fry nursery care, water-quality monitoring, health screening/vaccination, size grading, and transfer to open-water pens. Do not add instant one-click smolt purchases as a substitute for this lifecycle.
- Keep hatchery work hands-on and walkable, with readable, distinct incubator, nursery, fish-health lab, and grading/transfer stations.
- Treat the salmon pens as a first-class location, not a small decorative map prop. Show multiple unmistakable net pens with visible salmon, label them clearly, and make pen operations directly interactable.
- Keep the pens discoverable from the start: provide a persistent objective/compass cue and a clearly labeled minimap/map marker until the player reaches them.
- Make new locations and activities reinforce the working salmon-farm/coastal setting.
- Preserve existing farm-save migration and player progress. Do not overwrite legacy saves while adding features.

## Implementation and Verification

- The active game is `salmon_open_world.py`; `salmon_farm.py` is the launch entry point.
- Use Pygame CE from `requirements.txt`; retain nearest-neighbor pixel-art rendering.
- After changing farm locations, verify both their visual prominence and that the player can reach and interact with them.
- Test a complete smolt batch from egg intake through weekly stage changes, vaccination, grading, and transfer into the pen stock.
- Test the farming loop and save migration alongside movement/driving. A generic exploration or driving test alone is not sufficient.
- Keep the launch and control instructions in `README.md` current.
