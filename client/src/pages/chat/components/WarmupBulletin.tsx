import React from "react";
import { CoachState } from "@/types/coachState";
import { CoachingPhase } from "@/enums/coachingPhase";

/**
 * WarmupBulletin
 * Displays "Who You Are" and "Who You Want To Be" during the IDENTITY_WARMUP phase.
 *
 * Props:
 * - coachState: CoachState | null | undefined
 */
export const WarmupBulletin: React.FC<{ coachState: CoachState | null | undefined }> = ({ coachState }) => {
  const isWarmup = coachState?.current_phase === CoachingPhase.IDENTITY_WARMUP;
  if (!isWarmup) return null;

  return (
    <div className="mb-3 p-3 bg-gold-100 dark:bg-neutral-800 border border-gold-400 rounded-md">
      <div className="flex justify-between gap-4">
        <div className="flex-1">
          <div className="text-xs font-semibold text-gold-800 dark:text-gold-200 mb-1">Who You Are</div>
          {coachState?.who_you_are && coachState.who_you_are.length > 0 ? (
            <p className="text-xs text-neutral-800 dark:text-neutral-200 break-words">{coachState.who_you_are.join(", ")}</p>
          ) : (
            <p className="text-xs italic text-neutral-500 dark:text-neutral-400">Nothing yet...</p>
          )}
        </div>
        <div className="flex-1 text-right">
          <div className="text-xs font-semibold text-gold-800 dark:text-gold-200 mb-1">Who You Want To Be</div>
          {coachState?.who_you_want_to_be && coachState.who_you_want_to_be.length > 0 ? (
            <p className="text-xs text-neutral-800 dark:text-neutral-200 break-words">{coachState.who_you_want_to_be.join(", ")}</p>
          ) : (
            <p className="text-xs italic text-neutral-500 dark:text-neutral-400">Nothing yet...</p>
          )}
        </div>
      </div>
    </div>
  );
};


