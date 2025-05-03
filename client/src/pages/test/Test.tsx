import { useState } from 'react';
import { testStates } from '@/tests/testStates';
import TestStateSelector from '@/pages/test/components/TestStateSelector';
import TestChat from '@/pages/test/components/TestChat';

function Test() {
  const [selectedState, setSelectedState] = useState('');
  const [hasStarted, setHasStarted] = useState(false);

  if (hasStarted) {
    return (
      <TestChat
        selectedState={selectedState}
        setHasStarted={setHasStarted}
        testStates={testStates}
      />
    );
  }

  return (
    <div className="_Test flex items-start justify-center w-full h-full">
      <TestStateSelector
        selectedState={selectedState}
        setSelectedState={setSelectedState}
        setHasStarted={setHasStarted}
        testStates={testStates}
      />
    </div>
  );
}

export default Test;
