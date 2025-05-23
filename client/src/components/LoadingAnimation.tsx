export default function LoadingAnimation() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-700"></div>
      </div>
    </div>
  );
}
