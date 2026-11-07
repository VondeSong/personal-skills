# AI suggestions and review queues

Use for AI-assisted organization, cleanup, media management, or similar workflows. These rules describe UI behavior; they do not authorize changes to user data.

## State model

| State | Communicate | Typical action |
| --- | --- | --- |
| Ready | Capability and affected scope | Start, if needed |
| Running, total unknown | What is happening; indeterminate progress | Cancel if supported |
| Running, total known | Completed count and total using real data | Cancel/pause if supported |
| Suggestions ready | Proposed changes and their scope | Inspect, accept, reject, edit |
| Applying | Which accepted changes are executing | Cancel if safely supported |
| Partial completion | What succeeded, failed, and remains | Retry failed items or inspect |
| Completed | Actual result, including unresolved items | Undo/history when available |
| Failed / blocked | Cause, affected scope, and recovery | Retry, change input, resolve access |

A completed analysis is not completed execution. Counts must refer to the same stage as their labels.
Do not assume backend cancellation undoes changes already applied. Explain partial application when relevant.

## Presentation

Keep ordinary review states distinct from errors through text and a recognizable icon or control, not color alone.
Choose review prominence from the user's current goal. If reviewing is the whole task, the queue can be the primary content.
Show overview and review actions where the workflow makes them useful. There is no fixed upper-left/upper-right placement rule.
Reduce completed status emphasis after it has been perceivable, while keeping outcome and undo/history discoverable. Do not remove a result before assistive technology can convey it.
Avoid repetitive sparkle badges, decorative progress, and celebration that obscures the next decision.

## Decisions and recovery

Show the proposed change, affected objects/count, rationale when useful, and consequence of acceptance.
Separate suggestion, approval, and execution. Keep a way to reject or revise a suggestion without invoking the action.
Use undo for safely reversible edits. For irreversible batch operations, present precise scope and an explicit action verb at the decision boundary.
Preserve review selections and successful outcomes after a partial failure. Retrying failed items should not silently repeat completed operations.
