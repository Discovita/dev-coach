import React from "react";
import { ComponentConfig } from "@/types/componentConfig";
import { CoachRequest } from "@/types/coachRequest";
import { ComponentType } from "@/enums/componentType";
import { IntroCannedResponseComponent } from "./IntroCannedResponseComponent";
import { CombineIdentitiesConfirmation } from "./CombineIdentitiesConfirmation";

export interface CoachMessageWithComponentProps {
  children: React.ReactNode;
  componentConfig: ComponentConfig;
  onSendUserMessageToCoach: (request: CoachRequest) => void;
  disabled: boolean;
}

export const CoachMessageWithComponent: React.FC<
  CoachMessageWithComponentProps
> = ({ children, componentConfig, onSendUserMessageToCoach, disabled }) => {
  switch (componentConfig.component_type) {
    case ComponentType.INTRO_CANNED_RESPONSE:
      return (
        <IntroCannedResponseComponent
          coachMessage={children}
          config={componentConfig}
          onSendUserMessageToCoach={onSendUserMessageToCoach}
          disabled={disabled}
        />
      );
    case ComponentType.COMBINE_IDENTITIES:
      return (
        <CombineIdentitiesConfirmation
          coachMessage={children}
          config={componentConfig}
          onSendUserMessageToCoach={onSendUserMessageToCoach}
          disabled={disabled}
        />
      );
    default:
      return null;
  }
};
