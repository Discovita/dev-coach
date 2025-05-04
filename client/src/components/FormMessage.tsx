export type Message =
  | { success: string }
  | { error: string }
  | { message: string };

export function FormMessage({ message }: { message: Message }) {
  return (
    <div className="w-full">
      {"success" in message && (
        <div className="text-green-500 text-sm text-center bg-green-50 p-2 rounded-lg">
          {message.success}
        </div>
      )}
      {"error" in message && (
        <div className="text-red-500 text-sm text-center bg-red-50 p-2 rounded-lg mb-2">
          {message.error}
        </div>
      )}
      {"message" in message && (
        <div className="text-blue-500 text-sm text-center bg-blue-50 p-2 rounded-lg">
          {message.message}
        </div>
      )}
    </div>
  );
}
