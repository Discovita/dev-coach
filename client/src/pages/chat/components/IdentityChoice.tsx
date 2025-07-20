import React from "react";
import { Identity } from "@/types/identity";

export interface IdentityChoiceProps {
  identity: Identity;

  /**
   * Callback function when a button is clicked
   * @param response The predefined response text to send
   */
  onChoiceSelected: (response: string) => void;
  disabled: boolean;
}

export const IdentityChoice: React.FC<IdentityChoiceProps> = ({
  identity,
  onChoiceSelected,
  disabled,
}) => {
  return (
    <div className="identity-choice-buttons">
      <button
        onClick={() =>
          onChoiceSelected(
            `Yes, I like the "${identity.name}" identity.`
          )
        }
        disabled={disabled}
        className="identity-button accept-button"
        aria-label="Accept this identity"
      >
        I love it!
      </button>
      <button
        onClick={() =>
          onChoiceSelected(
            `I like this identity but can we adjust it slightly?`
          )
        }
        disabled={disabled}
        className="identity-button refine-button"
        aria-label="Refine this identity"
      >
        Refine it
      </button>
      <button
        onClick={() =>
          onChoiceSelected(
            `This isn't really what I'm looking for. What are some other options?`
          )
        }
        disabled={disabled}
        className="identity-button reject-button"
        aria-label="Try another identity"
      >
        Not for me
      </button>
    </div>
  );
};
