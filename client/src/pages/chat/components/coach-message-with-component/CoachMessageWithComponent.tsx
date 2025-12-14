import React from "react";
import { ComponentConfig } from "@/types/componentConfig";
import { CoachRequest } from "@/types/coachRequest";
import { ComponentType } from "@/enums/componentType";
import { IntroCannedResponseComponent } from "@/pages/chat/components/coach-message-with-component/IntroCannedResponseComponent";
import { CombineIdentitiesConfirmation } from "@/pages/chat/components/coach-message-with-component/CombineIdentitiesConfirmation";
import { NestIdentitiesConfirmation } from "@/pages/chat/components/coach-message-with-component/NestIdentitiesConfirmation";
import { ArchiveIdentityConfirmation } from "@/pages/chat/components/coach-message-with-component/ArchiveIdentityConfirmation";
import { SuggestIAmStatementComponent } from "@/pages/chat/components/coach-message-with-component/SuggestIAmStatementComponent";
import { IAmStatementsSummaryComponent } from "@/pages/chat/components/coach-message-with-component/IAmStatementsSummaryComponent";

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
    case ComponentType.NEST_IDENTITIES:
      return (
        <NestIdentitiesConfirmation
          coachMessage={children}
          config={componentConfig}
          onSendUserMessageToCoach={onSendUserMessageToCoach}
          disabled={disabled}
        />
      );
    case ComponentType.ARCHIVE_IDENTITY:
      return (
        <ArchiveIdentityConfirmation
          coachMessage={children}
          config={componentConfig}
          onSendUserMessageToCoach={onSendUserMessageToCoach}
          disabled={disabled}
        />
      );
    case ComponentType.SUGGEST_I_AM_STATEMENT:
      return (
        <SuggestIAmStatementComponent
          coachMessage={children}
          config={componentConfig}
          onSendUserMessageToCoach={onSendUserMessageToCoach}
          disabled={disabled}
        />
      );
    case ComponentType.I_AM_STATEMENTS_SUMMARY:
      return (
        <IAmStatementsSummaryComponent
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
