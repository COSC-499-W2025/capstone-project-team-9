"""
Portfolio Display Module

Handles displaying portfolio information in the CLI.
"""

from portfolio.portfolio_manager import PortfolioManager
from portfolio.portfolio_formatter import PortfolioFormatter


def display_portfolio(user_id: str = 'default_user', format_type: str = 'text', top_n: int = None):
    """
    Display analytical portfolio report.
    
    Args:
        user_id: User identifier
        format_type: Output format ('text', 'markdown')
        top_n: If specified, only show top N projects
    """
    print("\n" + "="*80)
    print("GENERATING PORTFOLIO REPORT...")
    print("="*80)
    print("Please wait, this may take a moment...\n")
    
    manager = PortfolioManager(user_id)
    
    # Generate portfolio report using existing functions
    portfolio_data = manager.generate_portfolio_report(top_n=top_n)
    
    if 'error' in portfolio_data:
        print(f"\nError generating portfolio: {portfolio_data['error']}")
        return
    
    # Format and display
    formatter = PortfolioFormatter()
    formatted = formatter.get_formatted_portfolio(portfolio_data, format_type)
    
    if formatted:
        print(formatted)
    else:
        print("Error formatting portfolio.")


def portfolio_menu():
    """Interactive menu for portfolio options."""
    print("\n" + "="*80)
    print("PORTFOLIO MENU")
    print("="*80)
    print("1. View full portfolio report (all projects)")
    print("2. View portfolio report (top 5 projects)")
    print("3. View portfolio report (top 10 projects)")
    print("4. Export portfolio as Markdown")
    print("5. Back to main menu")
    print("="*80)
    
    choice = input("Choose an option (1-5): ").strip()
    
    if choice == '1':
        display_portfolio()
        input("\nPress Enter to continue...")
    
    elif choice == '2':
        display_portfolio(top_n=5)
        input("\nPress Enter to continue...")
    
    elif choice == '3':
        display_portfolio(top_n=10)
        input("\nPress Enter to continue...")
    
    elif choice == '4':
        print("\nGenerating Markdown portfolio report...")
        manager = PortfolioManager()
        portfolio_data = manager.generate_portfolio_report()
        
        if 'error' not in portfolio_data:
            formatter = PortfolioFormatter()
            markdown_output = formatter.format_markdown(portfolio_data)
            
            if markdown_output:
                # Option to save to file
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save in ['y', 'yes']:
                    filename = input("Enter filename (default: portfolio_report.md): ").strip()
                    if not filename:
                        filename = "portfolio_report.md"
                    if not filename.endswith('.md'):
                        filename += '.md'
                    
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(markdown_output)
                        print(f"\nPortfolio report saved to {filename}")
                    except Exception as e:
                        print(f"\nError saving file: {e}")
                else:
                    print("\n" + markdown_output)
        else:
            print(f"\nError: {portfolio_data.get('error', 'Unknown error')}")
        
        input("\nPress Enter to continue...")
    
    elif choice == '5':
        return
    
    else:
        print("Invalid choice. Please enter 1-5.")