import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";

/**
 * StudioUnlockAnimation
 *
 * Full-screen, one-time takeover that plays when the user finishes the
 * identity visualization intro video (coaching complete). The Studio icon
 * appears with a padlock; the shackle pops open and swings, the lock falls
 * away and fades, and the icon lights up — "Your Studio is unlocked."
 *
 * There is intentionally NO Studio link here. Dismissing (Continue) reveals
 * the VisualizationChatGate underneath, which carries the actual
 * "Go to the Studio" button.
 *
 * The motion is a faithful port of the approved standalone prototype; the
 * keyframes live in the scoped <style> below.
 */
export const StudioUnlockAnimation: React.FC<{ onDismiss: () => void }> = ({
  onDismiss,
}) => {
  const continueRef = useRef<HTMLButtonElement>(null);

  // Allow Escape to dismiss, and focus the Continue button once it appears.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onDismiss();
    };
    window.addEventListener("keydown", onKey);
    const t = setTimeout(() => continueRef.current?.focus(), 2400);
    return () => {
      window.removeEventListener("keydown", onKey);
      clearTimeout(t);
    };
  }, [onDismiss]);

  return createPortal(
    <div
      className="suo-backdrop"
      role="dialog"
      aria-modal="true"
      aria-label="Your Studio is unlocked"
    >
      <style>{STYLES}</style>
      <div className="suo-scrim">
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
                stroke="#c7cbd4"
                strokeWidth="5"
                strokeLinecap="round"
              />
              <rect
                x="12"
                y="34"
                width="36"
                height="30"
                rx="6"
                fill="#3a3f4b"
                stroke="#c7cbd4"
                strokeWidth="3"
              />
              <circle cx="30" cy="47" r="4" fill="#c7cbd4" />
              <rect x="28.5" y="49" width="3" height="8" rx="1.5" fill="#c7cbd4" />
            </svg>
          </div>
        </div>

        <div className="suo-reveal">
          <h1>Your Studio is unlocked</h1>
          <p>You've finished building your identities. Time to bring them to life.</p>
          <button
            ref={continueRef}
            type="button"
            className="suo-continue"
            onClick={onDismiss}
          >
            Continue
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
};

const STYLES = `
  .suo-backdrop {
    position: fixed;
    inset: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background: radial-gradient(1200px 600px at 50% -10%, #1b1f2a, #0f1115);
    animation: suo-fadein 0.3s ease-out both;
  }
  @keyframes suo-fadein { from { opacity: 0; } to { opacity: 1; } }

  .suo-scrim {
    position: relative;
    width: 380px;
    max-width: 92vw;
    background: #1a1d24;
    border: 1px solid #2a2f3a;
    border-radius: 20px;
    padding: 40px 32px 32px;
    text-align: center;
    box-shadow: 0 30px 80px rgba(0,0,0,0.5);
    overflow: hidden;
    color: #e7e9ee;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    animation: suo-modalIn 0.45s cubic-bezier(.16,1,.3,1) both;
  }
  @keyframes suo-modalIn {
    from { opacity: 0; transform: translateY(12px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }

  .suo-stage { position: relative; width: 132px; height: 132px; margin: 8px auto 4px; }

  .suo-badge {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: rgba(124, 92, 255, 0.18);
    border: 1px solid rgba(124,92,255,0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #b9a8ff;
    animation: suo-badgeUnlock 0.8s ease-out 1.95s both;
  }
  .suo-badge svg { width: 56px; height: 56px; }
  @keyframes suo-badgeUnlock {
    0%   { filter: grayscale(0.6) brightness(0.8); transform: scale(1); }
    35%  { filter: grayscale(0) brightness(1.25); transform: scale(1.12); box-shadow: 0 0 0 0 #7c5cff; }
    100% { filter: grayscale(0) brightness(1.05); transform: scale(1); box-shadow: 0 0 36px 2px rgba(124,92,255,0.45); }
  }

  .suo-halo {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 2px solid #7c5cff;
    opacity: 0;
    animation: suo-halo 0.9s ease-out 2.0s both;
  }
  @keyframes suo-halo {
    0%   { opacity: 0.7; transform: scale(1); }
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

  .suo-scrim h1 { font-size: 21px; margin: 22px 0 6px; letter-spacing: -0.01em; }
  .suo-scrim p  { color: #9aa0ad; font-size: 14px; line-height: 1.5; margin: 0 0 22px; }
  .suo-reveal { opacity: 0; animation: suo-fadeUp 0.5s ease-out 2.25s both; }
  @keyframes suo-fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .suo-continue {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #7c5cff;
    color: white;
    border: none;
    font-weight: 600;
    font-size: 15px;
    padding: 12px 26px;
    border-radius: 12px;
    cursor: pointer;
  }
  .suo-continue:hover { filter: brightness(1.08); }

  @media (prefers-reduced-motion: reduce) {
    .suo-backdrop, .suo-scrim, .suo-badge, .suo-halo, .suo-reveal { animation: none; }
    .suo-lock { display: none; }
    .suo-reveal { opacity: 1; }
    .suo-badge { filter: none; }
  }
`;
