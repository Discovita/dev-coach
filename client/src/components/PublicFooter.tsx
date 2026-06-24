/**
 * PublicFooter
 *
 * Purpose:
 * - Footer used across public pages
 */
export default function PublicFooter() {
	return (
		<footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white py-16 relative overflow-hidden z-30">
			<div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-transparent to-indigo-900/10 z-0" />
			<div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl z-0" />
			<div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-500/5 rounded-full blur-3xl z-0" />

			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
				<div className="grid md:grid-cols-4 gap-12">
					<div className="md:col-span-1">
						<div className="flex items-center mb-6">
							<div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/25">
								<span className="text-white font-bold text-lg">D</span>
							</div>
							<span className="ml-3 text-2xl font-bold">Discovita</span>
						</div>
						<p className="text-gray-300 text-lg leading-relaxed">
							Transform your life through identity-driven coaching with
							AI-powered guidance.
						</p>
					</div>
					<div>
						<h3 className="font-semibold text-lg mb-6 text-white">Product</h3>
						<ul className="space-y-3 text-gray-300">
							<li>
								<a
									href="#"
									className="hover:text-white transition-colors duration-200 hover:translate-x-1 inline-block"
								>
									Features
								</a>
							</li>
							<li>
								<a
									href="#"
									className="hover:text-white transition-colors duration-200 hover:translate-x-1 inline-block"
								>
									Pricing
								</a>
							</li>
							<li>
								<a
									href="#"
									className="hover:text-white transition-colors duration-200 hover:translate-x-1 inline-block"
								>
									Demo
								</a>
							</li>
						</ul>
					</div>
					<div>
						<h3 className="font-semibold text-lg mb-6 text-white">Support</h3>
						<ul className="space-y-3 text-gray-300">
							<li>
								<a
									href="#"
									className="hover:text-white transition-colors duration-200 hover:translate-x-1 inline-block"
								>
									Help Center
								</a>
							</li>
							<li>
								<a
									href="#"
									className="hover:text-white transition-colors duration-200 hover:translate-x-1 inline-block"
								>
									Contact
								</a>
							</li>
							<li>
								<a
									href="#"
									className="hover:text-white transition-colors duration-200 hover:translate-x-1 inline-block"
								>
									Community
								</a>
							</li>
						</ul>
					</div>
					<div>
						<h3 className="font-semibold text-lg mb-6 text-white">Company</h3>
						<ul className="space-y-3 text-gray-300">
							<li>
								<a
									href="#"
									className="hover:text-white transition-colors duration-200 hover:translate-x-1 inline-block"
								>
									About
								</a>
							</li>
							<li>
								<a
									href="#"
									className="hover:text-white transition-colors duration-200 hover:translate-x-1 inline-block"
								>
									Blog
								</a>
							</li>
							<li>
								<a
									href="#"
									className="hover:text-white transition-colors duration-200 hover:translate-x-1 inline-block"
								>
									Careers
								</a>
							</li>
						</ul>
					</div>
				</div>
				<div className="border-t border-gray-700/50 mt-12 pt-8 text-center">
					<p className="text-gray-400 text-lg">
						&copy; 2025 Discovita. All rights reserved.
					</p>
				</div>
			</div>
		</footer>
	);
}
