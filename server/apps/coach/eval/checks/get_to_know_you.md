# Targeted checks for the get_to_know_you phase.
#
# Explicit, hand-authored pass/fail assertions the judge evaluates IN ADDITION
# to the prompt-derived rubric — the "this phase must do X / must never do Y"
# cases you care about, including things the prompt may not spell out.
#
# One check per line. Blank lines and lines starting with '#' are ignored; a
# single leading '-' bullet is stripped. Keep each check a single, unambiguous,
# yes/no statement about the COACH's behavior.

- The coach never asks more than one question in a single message.
- The coach never invents or assumes facts about the client that the client did not actually say.
- The coach builds on what the client just shared rather than asking generic, disconnected questions.
- The coach does not begin Identity work (brainstorming or naming identities) during this phase.
- The coach never re-asks or re-opens a topic already covered in the Asked-Questions list, even in reworded form.
