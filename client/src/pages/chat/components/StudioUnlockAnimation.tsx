import { Dialog as DialogPrimitive } from "radix-ui";
import { Button } from "@/components/ui/button";

/**
 * StudioUnlockAnimation
 *
 * One-time modal that plays when the user finishes the identity visualization
 * intro video (coaching complete). The Studio icon appears with a padlock; the
 * shackle pops open and swings, the lock falls away and fades, and the icon
 * lights up — "Your Studio is unlocked."
 *
 * Deliberately a light popover that floats over the chat with a TRANSPARENT
 * backdrop, so the chat window stays fully visible behind it — we are not
 * taking the user out of the chat, just surfacing a moment. There is no Studio
 * link here; dismissing (Continue / Escape / click-outside) reveals the
 * VisualizationChatGate underneath, which carries the "Go to the Studio"
 * button.
 *
 * The lock motion is a faithful port of the approved prototype (scoped
 * keyframes below); the card entrance is Radix's standard zoom/fade.
 */
export const StudioUnlockAnimation: React.FC<{ onDismiss: () => void }> = ({
  onDismiss,
}) => {
  return (
    <DialogPrimitive.Root
      open
      onOpenChange={(next) => {
        if (!next) onDismiss();
      }}
    >
      <DialogPrimitive.Portal>
        {/* Soft overlay: a light fade + blur (not a heavy dark dim) so the
            chat stays recognizable behind it but the modal is clearly the
            focus and the user understands they must click Continue. */}
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-white/40 backdrop-blur-sm data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=closed]:animate-out data-[state=closed]:fade-out-0" />
        <DialogPrimitive.Content
          className="fixed top-1/2 left-1/2 z-50 grid w-full max-w-sm -translate-x-1/2 -translate-y-1/2 justify-items-center gap-4 rounded-xl border bg-background p-7 text-center shadow-2xl outline-none ring-1 ring-black/5 duration-200 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95"
        >
          <style>{STYLES}</style>
          <div className="suo-stage">
            <div className="suo-halo" />
            <div className="suo-badge">
              {/* studio (brush) icon */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="m9.06 11.9 8.07-8.06a2.85 2.85 0 1 1 4.03 4.03l-8.06 8.08" />
                <path d="M7.07 14.94c-1.66 0-3 1.35-3 3.02 0 1.33-2.5 1.52-2 2.02 1.08 1.1 2.49 2.02 4 2.02 2.2 0 4-1.8 4-4.04a3.01 3.01 0 0 0-3-3.02z" />
              </svg>
            </div>

            {/* lock sitting on top of the badge */}
            <div className="suo-lock">
              <svg viewBox="0 0 60 72" fill="none">
                <path
                  className="suo-shackle"
                  d="M18 42 V22 a12 12 0 0 1 24 0 V42"
                  stroke="#94a3b8"
                  strokeWidth="5"
                  strokeLinecap="round"
                />
                <rect
                  x="12"
                  y="34"
                  width="36"
                  height="30"
                  rx="6"
                  fill="#e2e8f0"
                  stroke="#94a3b8"
                  strokeWidth="3"
                />
                <circle cx="30" cy="47" r="4" fill="#64748b" />
                <rect x="28.5" y="49" width="3" height="8" rx="1.5" fill="#64748b" />
              </svg>
            </div>
          </div>

          <div className="suo-reveal flex flex-col items-center text-center gap-2">
            <DialogPrimitive.Title className="text-xl font-semibold text-[color:var(--nv-royal-purple)]">
              Your Studio is unlocked
            </DialogPrimitive.Title>
            <DialogPrimitive.Description className="text-sm text-muted-foreground max-w-xs">
              You've finished building your identities. Time to bring them to life.
            </DialogPrimitive.Description>
            <Button type="button" className="mt-3" onClick={onDismiss}>
              Continue
            </Button>
          </div>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
};

const STYLES = `
  .suo-stage { position: relative; width: 132px; height: 132px; margin: 8px auto 4px; }

  .suo-badge {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: var(--nv-pale-lavender, #eae6fb);
    border: 1px solid rgba(83, 30, 150, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--nv-royal-purple, #531e96);
    animation: suo-badgeUnlock 0.8s ease-out 1.95s both;
  }
  .suo-badge svg { width: 56px; height: 56px; }
  @keyframes suo-badgeUnlock {
    0%   { filter: grayscale(0.6) brightness(1.05); transform: scale(1); }
    35%  { filter: grayscale(0) brightness(1); transform: scale(1.12); box-shadow: 0 0 0 0 rgba(106,95,251,0.6); }
    100% { filter: grayscale(0) brightness(1); transform: scale(1); box-shadow: 0 0 34px 2px rgba(106,95,251,0.45); }
  }

  .suo-halo {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 2px solid var(--nv-violet-blue, #6a5ffb);
    opacity: 0;
    animation: suo-halo 0.9s ease-out 2.0s both;
  }
  @keyframes suo-halo {
    0%   { opacity: 0.6; transform: scale(1); }
    100% { opacity: 0;   transform: scale(1.6); }
  }

  .suo-lock {
    position: absolute;
    left: 50%;
    top: 56%;
    width: 60px;
    height: 72px;
    transform: translate(-50%, -50%);
    animation: suo-lockFall 0.85s cubic-bezier(.5,.05,.9,.4) 1.55s both;
  }
  .suo-lock svg { width: 100%; height: 100%; overflow: visible; }
  .suo-shackle {
    transform-box: fill-box;
    transform-origin: 100% 100%;
    animation: suo-shackleOpen 0.55s cubic-bezier(.34,1.56,.64,1) 1.0s both;
  }
  @keyframes suo-shackleOpen {
    0%   { transform: translateY(0)    rotate(0deg); }
    35%  { transform: translateY(-7px) rotate(0deg); }
    100% { transform: translateY(-5px) rotate(42deg); }
  }
  @keyframes suo-lockFall {
    0%   { transform: translate(-50%, -50%) rotate(0deg); opacity: 1; }
    20%  { transform: translate(-50%, -54%) rotate(-4deg); opacity: 1; }
    100% { transform: translate(-46%, 90%) rotate(22deg); opacity: 0; }
  }

  .suo-reveal { opacity: 0; animation: suo-fadeUp 0.5s ease-out 2.25s both; }
  @keyframes suo-fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
`;
