//
//  APIService.swift
//  MoneyInOne
//
//  Created by AI Frontend Master on 2025/10/1.
//

import Foundation

/// API Environment Configuration
enum APIEnvironment {
    case development
    case production
    
    var baseURL: String {
        switch self {
        case .development:
            #if targetEnvironment(simulator)
            return "http://localhost:8000/api/v1"
            #else
            // For testing on physical device with local network
            return "http://192.168.1.2:8000/api/v1"
            #endif
        case .production:
            return "https://moneyinone-api.onrender.com/api/v1"
        }
    }
}

/// API configuration
struct APIConfig {
    // MARK: - Configuration
    
    /// Current environment - Change this to switch between dev and prod
    /// Set to .production before App Store submission
    static let currentEnvironment: APIEnvironment = .production
    
    static var baseURL: String {
        print("🌐 API URL: \(currentEnvironment.baseURL)")
        return currentEnvironment.baseURL
    }
    
    static let timeout: TimeInterval = 30
    
    // MARK: - Helper Methods
    
    /// Check if running in development mode
    static var isDevelopment: Bool {
        return currentEnvironment == .development
    }
    
    /// Check if running in production mode
    static var isProduction: Bool {
        return currentEnvironment == .production
    }
}

/// API errors
enum APIError: LocalizedError {
    case networkError(Error)
    case invalidResponse
    case serverError(Int, String)
    case decodingError(Error)
    case invalidURL
    case missingData
    
    var errorDescription: String? {
        switch self {
        case .networkError(let error):
            return "Network connection failed: \(error.localizedDescription)"
        case .invalidResponse:
            return "Invalid response from server."
        case .serverError(let code, let message):
            return "Server error (\(code)): \(message)"
        case .decodingError(let error):
            return "Failed to parse response data: \(error.localizedDescription)"
        case .invalidURL:
            return "Invalid URL."
        case .missingData:
            return "No data received from server."
        }
    }
}

/// Generic API response wrapper
struct APIResponse<T: Codable>: Codable {
    let message: String
    let data: T?
}

/// Success response
struct SuccessResponse: Codable {
    let message: String
}

/// Base API service
class APIService {
    // MARK: - Properties
    
    static let shared = APIService()
    
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    
    // MARK: - Initialization
    
    private init() {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = APIConfig.timeout
        session = URLSession(configuration: configuration)
        
        // Configure decoder for ISO 8601 dates
        decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)
            
            // Try ISO 8601 with fractional seconds first
            if let date = DateFormatter.iso8601.date(from: dateString) {
                return date
            }
            
            // Try standard ISO 8601 without fractional seconds
            let formatter = ISO8601DateFormatter()
            if let date = formatter.date(from: dateString) {
                return date
            }
            
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Cannot decode date string: \(dateString)"
            )
        }
        
        // Configure encoder for ISO 8601 dates
        encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
    }
    
    // MARK: - Public Methods
    
    /// Performs a GET request
    func get<T: Codable>(
        endpoint: String,
        queryItems: [URLQueryItem]? = nil
    ) async throws -> T {
        let request = try buildRequestWithoutBody(
            endpoint: endpoint,
            method: "GET",
            queryItems: queryItems
        )
        
        return try await performRequest(request)
    }
    
    /// Performs a POST request with body
    func post<T: Codable, B: Encodable>(
        endpoint: String,
        body: B,
        queryItems: [URLQueryItem]? = nil,
        headers: [String: String]? = nil
    ) async throws -> T {
        let request = try buildRequestWithBody(
            endpoint: endpoint,
            method: "POST",
            body: body,
            queryItems: queryItems,
            headers: headers
        )
        
        return try await performRequest(request)
    }
    
    /// Performs a POST request without body
    func post<T: Codable>(
        endpoint: String,
        queryItems: [URLQueryItem]? = nil,
        headers: [String: String]? = nil
    ) async throws -> T {
        let request = try buildRequestWithoutBody(
            endpoint: endpoint,
            method: "POST",
            queryItems: queryItems,
            headers: headers
        )
        
        return try await performRequest(request)
    }
    
    /// Performs a PUT request
    func put<T: Codable, B: Encodable>(
        endpoint: String,
        body: B,
        queryItems: [URLQueryItem]? = nil
    ) async throws -> T {
        let request = try buildRequestWithBody(
            endpoint: endpoint,
            method: "PUT",
            body: body,
            queryItems: queryItems
        )
        
        return try await performRequest(request)
    }
    
    /// Performs a DELETE request
    func delete<T: Codable>(
        endpoint: String,
        queryItems: [URLQueryItem]? = nil
    ) async throws -> T {
        let request = try buildRequestWithoutBody(
            endpoint: endpoint,
            method: "DELETE",
            queryItems: queryItems
        )
        
        return try await performRequest(request)
    }
    
    // MARK: - Private Methods
    
    private func buildRequestWithBody<B: Encodable>(
        endpoint: String,
        method: String,
        body: B,
        queryItems: [URLQueryItem]? = nil,
        headers: [String: String]? = nil
    ) throws -> URLRequest {
        guard var urlComponents = URLComponents(string: "\(APIConfig.baseURL)\(endpoint)") else {
            throw APIError.invalidURL
        }
        
        if let queryItems = queryItems, !queryItems.isEmpty {
            urlComponents.queryItems = queryItems
        }
        
        guard let url = urlComponents.url else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Add additional headers
        headers?.forEach { key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }
        
        // Encode body
        request.httpBody = try encoder.encode(body)
        
        return request
    }
    
    private func buildRequestWithoutBody(
        endpoint: String,
        method: String,
        queryItems: [URLQueryItem]? = nil,
        headers: [String: String]? = nil
    ) throws -> URLRequest {
        guard var urlComponents = URLComponents(string: "\(APIConfig.baseURL)\(endpoint)") else {
            throw APIError.invalidURL
        }
        
        if let queryItems = queryItems, !queryItems.isEmpty {
            urlComponents.queryItems = queryItems
        }
        
        guard let url = urlComponents.url else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Add additional headers
        headers?.forEach { key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }
        
        return request
    }
    
    private func performRequest<T: Codable>(_ request: URLRequest) async throws -> T {
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }
            
            // Log request and response for debugging
            print("🌐 API Request: \(request.httpMethod ?? "UNKNOWN") \(request.url?.absoluteString ?? "")")
            print("📥 Response Status: \(httpResponse.statusCode)")
            
            if let responseBody = String(data: data, encoding: .utf8) {
                print("📦 Response Body: \(responseBody)")
            }
            
            // Handle different status codes
            switch httpResponse.statusCode {
            case 200...299:
                // Success - decode response
                do {
                    let decoded = try decoder.decode(T.self, from: data)
                    return decoded
                } catch {
                    print("❌ Decoding error: \(error)")
                    throw APIError.decodingError(error)
                }
                
            case 400...499:
                // Client error
                if let errorMessage = try? decoder.decode([String: String].self, from: data),
                   let detail = errorMessage["detail"] {
                    throw APIError.serverError(httpResponse.statusCode, detail)
                }
                throw APIError.serverError(httpResponse.statusCode, "Client error")
                
            case 500...599:
                // Server error
                if let errorMessage = try? decoder.decode([String: String].self, from: data),
                   let detail = errorMessage["detail"] {
                    throw APIError.serverError(httpResponse.statusCode, detail)
                }
                throw APIError.serverError(httpResponse.statusCode, "Server error")
                
            default:
                throw APIError.invalidResponse
            }
        } catch let error as APIError {
            throw error
        } catch {
            throw APIError.networkError(error)
        }
    }
}

